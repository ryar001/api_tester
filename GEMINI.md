
## TODO
- everytime u learn more about the project, update a PLANNING.md, create one if not available
- if `ai-tracker` is called, read the AI_TRACKER_GENIE.md file

## for every task
### Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints. Create one at root if not available
- **Check `TASK.md`** before starting a new task. If the task isn’t listed, add it with a brief description and today's date. Create one at root if not available
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.

### Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).
- For common key name , create a constant file and clearly categories each constant by who is using them for when it output data, eg, for the name of keys from API response
- **Try to use Typed dict when dict is used**
- clear state why data will be returned, if arbitrary data, eg , dataframe of list with a lot random data type is returned, create a item class in another file and return that instead
- Always write code with testability in mind
- write pure function/method whenever possible
- use dependency injection whenever possible

### When writing/updating a file for packages
- go through the api documentation and make sure all possible parameters are covered
    - then map the methods to a concise summary of what it does with its inputs data and outputs data
    - then write/update the methods requested
        - make sure the method written is available in the package, do not hallucinate a new method
    - then update the unit test to cover all the methods
        - if it requires api_key, ask the user for one else add a mock test that doesn't call the api
        - if it doesn't require api_key, add a live test that calls the api
        - if calls failed, add a test for that as well and just alert the user which method failed and the errors
- if not asked to add new methods, just update the methods that are already in place, no need to add new methods
- always check the inputs is correct

### Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case

### ✅ Task Completion
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a “Discovered During Work” section.

### 📎 Style & Conventions
- **Use Python** as the primary language.
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- Use `FastAPI` for APIs and `SQLAlchemy` or `SQLModel` for ORM if applicable.
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

### AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.
- **If editing current file, make a git commit -m "WIP" before editing {CURRENT_FILE} FOR {REASON}**