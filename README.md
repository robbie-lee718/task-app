# TaskApp
This is a small personal project for use of better understanding and using SQL queries via sqlite.

## Desktop Application
To run the UI application of TaskAPP run
`python ui.app`
in the terminal.

## CLI

Add Task: `python cli.app add "{TASK NAME}" -d "{TASK DESCRIPTION}"`

Delete Task: `python cli.app delete {ROW ID}`

Update Task: `python cli.app update {ROW ID} -n {TASK NAME} -d {TASK DESCRIPTION}`<br><span style="color: gray;">*Note: Including task name or task description is optional*</span>

List Tasks: `python cli.app list`

## Requirements
### UI
Must have PyQt5 installed!!!


How to install PyQt5:


`python -m venv myenv`


`source myenv/bin/activate`

<span style="color: gray;">*Note: Not required to create and source venv but advised to avoid incompatible versions*</span>


`pip install pyqt5`

### CLI & UI
Must have python installed on machine.
