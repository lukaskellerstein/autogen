db = new Mongo().getDB("AutogenDB");

db.createCollection("tenants");
db.tenants.insert({ name: "companyABC" });

db.createCollection("users");
db.users.insert({
  name: "daniel_superman",
  tenant: "companyABC",
  teams: ["my_first_team"],
});

db.createCollection("teams");
db.teams.insert({
  name: "my_first_team",
  members: [
    // { name: "groupchat_manager", role: "group_chat" },
    {
      name: "user_proxy-me",
      role: "user_proxy",
      system_message: "A human admin.",
    },
    {
      name: "assistant1-coder",
      role: "assistant",
      system_message: `You are a helpful AI assistant.
    Solve tasks using your coding and language skills.
    In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute.
        1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
        2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly.
    Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill.
    When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user.
    If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
    If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
    When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
    Reply "TERMINATE" in the end when everything is done.`,
    },
    {
      name: "assistant2-product_manager",
      role: "assistant",
      system_message: "Creative in software product ideas.",
    },
  ],
});

db.createCollection("chats");
db.chats.insert({
  name: "abcd1234",
  user: "daniel_superman",
  team: "my_first_team",
  state: {
    groupchat_manager: {},
    "user_proxy-me": {},
    "assistant1-coder": {},
    "assistant2-product_manager": {},
  },
});
