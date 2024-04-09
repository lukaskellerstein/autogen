from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union
from autogen.db_utils import MongoDbService

from autogen.oai.client import OpenAIWrapper
import logging
import nats
import json
import copy

try:
    from termcolor import colored
except ImportError:

    def colored(x, *args, **kwargs):
        return x

logger = logging.getLogger(__name__)


@dataclass
class DGroupChat:
    """(In preview) A group chat class that contains the following data fields:
    - agents: a list of participating agents.
    - messages: a list of messages in the group chat.
    - max_round: the maximum number of rounds.
    - admin_name: the name of the admin agent if there is one. Default is "Admin".
        KeyBoardInterrupt will make the admin agent take over.
    - func_call_filter: whether to enforce function call filter. Default is True.
        When set to True and when a message is a function call suggestion,
        the next speaker will be chosen from an agent which contains the corresponding function name
        in its `function_map`.
    """

    agents: List[Dict[str, Any]]
    messages: List[Dict]
    max_round: int = 10
    admin_name: str = "Admin"
    func_call_filter: bool = True

    @property
    def agent_names(self) -> List[str]:
        """Return the names of the agents in the group chat."""
        return [agent["name"] for agent in self.agents]

    def reset(self):
        """Reset the group chat."""
        self.messages.clear()

    def agent_by_name(self, name: str) -> Dict[str, Any]:
        """Find the next speaker based on the message."""
        return self.agents[self.agent_names.index(name)]

    # def next_agent(self, agent: str, agents: List[Dict[str, Any]]) -> str:
    #     """Return the next agent in the list."""
    #     if agents == self.agents:
    #         return agents[(self.agents.index(agent['name']) + 1) % len(agents)]
    #     else:
    #         offset = self.agents.index(agent['name']) + 1
    #         for i in range(len(self.agents)):
    #             if self.agents[(offset + i) % len(self.agents)] in agents:
    #                 return self.agents[(offset + i) % len(self.agents)]
                
    def next_agent(self, agent: Dict[str, Any], agents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return the next agent in the list."""
        agent_names = [a['name'] for a in self.agents]
        if [a['name'] for a in agents] == agent_names:
            return agents[(agent_names.index(agent['name']) + 1) % len(agents)]
        else:
            offset = agent_names.index(agent['name']) + 1
            for i in range(len(self.agents)):
                if self.agents[(offset + i) % len(self.agents)]['name'] in [a['name'] for a in agents]:
                    return self.agents[(offset + i) % len(self.agents)]

    def select_speaker_msg(self, agents: List[str]):
        """Return the message for selecting the next speaker."""
        return f"""
        You are in a role play game. The following roles are available: 
        {self._participant_roles()}

        Read the following conversation.
        Then select the next role from {[agent['name'] for agent in agents]} to play. Only return the role."""

    # def _participant_roles(self):



    def _participant_roles(self):
        return "\n".join([f"{i}. {agent['name']}: {agent['system_message']}" for i, agent in enumerate(self.agents)])
    
    def user_proxy(self):
        def is_user_proxy(obj):
            return obj["role"] == "user_proxy"

        # Filtering using filter()
        filtered_objects = list(filter(is_user_proxy, self.agents))
        return filtered_objects[0]


class DGroupChatManager():
    """(In preview) A chat manager agent that can manage a group chat of multiple agents."""

    def __init__(
        self,
        groupchat: DGroupChat,
        name: Optional[str] = "chat_manager",
        llm_config: Union[Dict, bool] = None,
        broker_config: Dict = None,
        db_config: Dict = None,
    ):
        self.groupchat = groupchat
        self.name = name

        #NOTE: Do we need? ---------
        self._oai_messages = defaultdict(list)
        self._oai_system_message = [{"content": "", "role": "system"}]
        # --------------------------

        self.llm_config = llm_config
        self.client = OpenAIWrapper(**llm_config)

        self.broker_config = broker_config
        self.db_config = db_config

        self.current_round = 0

        self.db = MongoDbService(db_config["name"], db_config["url"], db_config["port"], db_config["user"], db_config["password"])


    async def subscribe(self):
        print("broker config", self.broker_config)

        self.broker = await nats.connect(f"nats://{self.broker_config['url']}", user=self.broker_config["user"], password=self.broker_config["password"])
        print(f"Connected to NATS at {self.broker.connected_url.netloc}...")


        async def subscribe_handler(msg):
            subject = msg.subject
            reply = msg.reply
            data = json.loads(msg.data.decode())

            print("--------------------------------------")
            print(f"[[[[[[[[[{self.name}]]]]]]]]]")
            print("--------------------------------------")
            print("BROKER MESSAGE RECEIVED:")
            print(f"{self.name} <<<<<<<<<<<<<<<<<<<<<<<<< {data['sender']}")
            print("subject: ", subject)
            print("action: ", data["action"])
            print("message: ", data["payload"]["message"])
            print("--------------------------------------")

            # Store message into DB --------------
            chatId = subject.split(".")[3]
            print("chatId: ", chatId)
            self.db.insert_message(chatId, {
                "sender": data["sender"],
                "action": data["action"],
                "payload": data["payload"],
            })
            # ------------------------------------

            if data["action"] == "init_chat":
                # self.current_round += 1

                # --------------------------------------------
                # reset the group chat and all agents
                self._oai_messages = defaultdict(list)
                self.groupchat.reset()
                for agent in self.groupchat.agents:
                    reply_message = {
                        "sender": self.name,
                        "action": "reset",
                    }
                    await self.publish(subject, recipient=agent["name"], message=reply_message)

                # --------------------------------------------
                # first speaker is always the user_proxy
                speaker = self.groupchat.user_proxy()

                #NOTE: FINISH
                # OBJECT TRANSFORMATION
                reply_message = {
                    "sender": self.name,
                    "action": "save_message",
                    "payload": {
                        "message": {
                            "role": "assistant",
                            "content": data["payload"]["message"],
                        },
                    }
                }

                await self.publish(subject, recipient=speaker["name"], message=reply_message)
                # --------------------------------------------

                new_message = {
                    "role": "user",
                    "name": speaker["name"],
                    "content": data["payload"]["message"],
                }

                # store the message
                self._oai_messages[speaker["name"]].append(new_message)

                deep_copied_new_message = copy.deepcopy(new_message)
                await self.run_chat(subject, deep_copied_new_message, speaker)
            

            if data["action"] == "reply":
                self.current_round += 1
                
                if(self.current_round > self.groupchat.max_round):
                    print("--------------------------")
                    print("--------------------------")
                    print("Chat is over. !!!!!!!! self.current_round > self.groupchat.max_round")
                    print("--------------------------")
                    print("--------------------------")
                    # end the chat
                    return


                agent = self.groupchat.agent_by_name(data["sender"])

                check_termination = self.check_termination(data["payload"]["message"], data["sender"])

                if check_termination:
                    print("--------------------------")
                    print("--------------------------")
                    print("Chat is over. !!!!!!!! TERMINATE")
                    print("--------------------------")
                    print("--------------------------")
                    # end the chat
                    return

                #NOTE: FINISH
                # OBJECT TRANSFORMATION
                new_message = {
                    "role": "user",
                    "content": data["payload"]["message"],
                }

                # store the message
                self._oai_messages[agent["name"]].append(new_message)


                await self.run_chat(subject, new_message, agent)


        # Basic subscription to receive all published messages
        # which are being sent to a single topic 'discover'
        await self.broker.subscribe(f"*.*.*.*.{self.name}", cb=subscribe_handler)

    async def publish(self, subject:str, recipient: str, message: Dict[str, Any]):

        new_subject = f"{subject.split('.')[0]}.{subject.split('.')[1]}.{subject.split('.')[2]}.{subject.split('.')[3]}.{recipient}"

        print("--------------------------------------")
        print(f"[[[[[[[[[{self.name}]]]]]]]]]")
        print("--------------------------------------")
        print("MESSAGE SEND:")
        print(f"{self.name} >>>>>>>>>>>>>>> {recipient}")
        print("action ", message["action"])
        print("message ", message)
        print("--------------------------------------")
        print("This OAI messages:")
        for k, v in self._oai_messages.items():
            print(k)
            for msg in v:
                print(msg)
        print("--------------------------------------")

        serialized_message = json.dumps(message).encode('utf-8')
        await self.broker.publish(new_subject, serialized_message)


    def select_speaker(self, last_speaker: Dict[str, Any]):
        """Select the next speaker."""
        if self.groupchat.func_call_filter and self.groupchat.messages and "function_call" in self.groupchat.messages[-1]:
            # find agents with the right function_map which contains the function name
            agents = [
                agent for agent in self.groupchat.agents if self.groupchat.messages[-1]["function_call"]["name"] in agent["function_map"]
            ]
            if len(agents) == 1:
                # only one agent can execute the function
                return agents[0]
            elif not agents:
                # find all the agents with function_map
                agents = [agent for agent in self.groupchat.agents if len(agent["function_map"]) > 0]
                if len(agents) == 1:
                    return agents[0]
                elif not agents:
                    raise ValueError(
                        f"No agent can execute the function {self.groupchat.messages[-1]['name']}. "
                        "Please check the function_map of the agents."
                    )
        else:
            agents = self.groupchat.agents

            print("agents")
            print(agents)
            print("last_speaker")
            print(last_speaker)

            if len(agents) == 2:
                return self.groupchat.next_agent(last_speaker, agents)

            # Warn if GroupChat is underpopulated
            # n_agents = len(agents)
            # if n_agents < 3:
            #     logger.warning(
            #         f"GroupChat is underpopulated with {n_agents} agents. Direct communication would be more efficient."
            #     )
        
        speaker_msg = self.groupchat.select_speaker_msg(agents)

        print("speaker_msg")
        print(speaker_msg)

        self.update_system_message(speaker_msg)

        msgs = [
                {
                    "role": "system",
                    "content": speaker_msg,
                }
            ] + self.groupchat.messages

        print("--------------------------------------")
        print("SELECT SPEAKER MESSAGES")
        print(msgs)
        print("--------------------------------------")

        final, name = self.generate_oai_reply(msgs)

        
        print("--------------------------------------")
        print("[select_speaker] OAI response: ", name)
        print("GroupChat messages:")
        for msg in self.groupchat.messages:
            print(msg)
        print("--------------------------------------")
        

        if not final:
            # i = self._random.randint(0, len(self._agent_names) - 1)  # randomly pick an id
            return self.groupchat.next_agent(last_speaker, agents)
        try:
            return self.groupchat.agent_by_name(name)
        except ValueError:
            logger.warning(
                f"GroupChat select_speaker failed to resolve the next speaker's name. Speaker selection will default to the next speaker in the list. This is because the speaker selection OAI call returned:\n{name}"
            )
            return self.groupchat.next_agent(last_speaker, agents)

    async def run_chat(
        self,
        subject: str,
        message: Dict,
        speaker: Dict[str, Any],
    ) -> Union[str, Dict, None]:
        """Run a group chat."""



        print("-----------------------------------------------------------------")
        print(f"------------------ Round {self.current_round} ------------------")
        print("-----------------------------------------------------------------")
        


        # set the name to speaker's name if the role is not function
        if message["role"] != "function":
            message["name"] = speaker["name"]

        self.groupchat.messages.append(message)

        print("GroupChat messages:")
        for msg in self.groupchat.messages:
            print(msg)
        print("--------------------------------------")


        # broadcast the message to all agents except the speaker
        print("------------------ BROADCASTING --------------------")
        for agent in self.groupchat.agents:
            if agent["name"] != speaker["name"]:

                new_message = copy.deepcopy(message)

                #HACK: change message role to "assistant" for all broadcasted messages
                new_message["role"] = "assistant"

                self._oai_messages[agent["name"]].append(new_message)

                broker_message = {
                    "sender": self.name,
                    "action": "save_message",
                    "payload": {
                        "message": new_message,
                    }
                }

                await self.publish(subject, recipient=agent["name"], message=broker_message)
        print("----------------------------------------------------")

        try:
            # select the next speaker 
            speaker = self.select_speaker(speaker)
            
            #NOTE: FINISH
            # reply = speaker.generate_reply(sender=self)
            new_message = {
                "sender": self.name,
                "action": "generate_reply",
                "payload": {
                        "message": message,
                    }
            }

            await self.publish(subject, recipient=speaker["name"], message=new_message)

        except KeyboardInterrupt:
            # let the admin agent speak if interrupted
            if self.groupchat.admin_name in self.groupchat.agent_names:
                # admin agent is one of the participants
                speaker = self.groupchat.agent_by_name(self.groupchat.admin_name)

                #NOTE: FINISH !!!
                # reply = speaker.generate_reply(sender=self)
            else:
                # admin agent is not found in the participants
                raise
        # if reply is None:
        #     break



    def update_system_message(self, system_message: str):
        """Update the system message.

        Args:
            system_message (str): system message for the ChatCompletion inference.
        """
        self._oai_system_message[0]["content"] = system_message


    def generate_oai_reply(
        self,
        messages: List[Dict],
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using autogen.oai."""

        print("--------------------------------------")
        print("--------------------------------------")
        print("--------------------------------------")
        print("--------------------------------------")
        # aaa = self._oai_system_message + messages
        aaa = messages
        for a in aaa:
            print(a)
        print("--------------------------------------")
        print("--------------------------------------")
        print("--------------------------------------")
        print("--------------------------------------")
        
        # TODO: #1143 handle token limit exceeded error
        response = self.client.create(
            context=messages[-1].pop("context", None), messages=aaa
        )

        text_or_function_call = self.client.extract_text_or_function_call(response)[0]

        # print(text_or_function_call)

        return True, text_or_function_call




    def get_human_input(self, prompt: str) -> str:
        """Get human input.

        Override this method to customize the way to get human input.

        Args:
            prompt (str): prompt for the human input.

        Returns:
            str: human input.
        """
        reply = input(prompt)
        return reply

    def check_termination(self, message: Dict, sender: str) -> bool:
        """Check if the chat is terminated."""

        reply = ""
        no_human_input_msg = ""

        isTerminated = message.lower() == "terminate"

        if isTerminated:
            reply = self.get_human_input(
                        f"Please give feedback to {sender}. Press enter or type 'exit' to stop the conversation: "
                    )
            no_human_input_msg = "NO HUMAN INPUT RECEIVED." if not reply else ""
            # if the human input is empty, and the message is a termination message, then we will terminate the conversation
            reply = reply or "exit"

        # print the no_human_input_msg
        if no_human_input_msg:
            print(colored(f"\n>>>>>>>> {no_human_input_msg}", "red"), flush=True)

        # stop the conversation
        if reply == "exit":
            # reset the consecutive_auto_reply_counter
            self._consecutive_auto_reply_counter[sender] = 0
            return True
        
        return False
