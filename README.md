# TaskApp
This is a small personal project for use of better understanding and using SQL queries via sqlite.


Arguments for cli commands can be found below:

Add Task: `python cli.app add "{TASK NAME}" -d "{TASK DESCRIPTION}"`

Delete Task: `python cli.app delete {ROW ID}`

Update Task: `python cli.app update {ROW ID} -n {TASK NAME} -d {TASK DESCRIPTION}`<br><span style="color: gray;">*Note: Including task name or task description is optional*</span>

List Tasks: `python cli.app list`