# pricepy
Welcome! 123

## Git commit principles
In this project, **we create commits with the compliance to the rules below:**

##### Tags:
- every commit **should contain at least one tag** from the list: [APP, CRAWLER, ML_MODEL, GLOBAL] - accordingly to the code place in which the changes have been implemented
- the tags are provided at the beginning of the commit in square brackets: [CRAWLER] ...commit message...

##### Types:
- every commit **should specify what kind of changes have been implemented.** In order to do that, we specify the commit type after the tag: [APP] feat: ...commit message...
- a list of possible commit types: [feat, fix, chore, refactor, docs, style, test, perf, ci, build, revert]. More details [here](https://www.freecodecamp.org/news/how-to-write-better-git-commit-messages/).

##### Tags/types mixing:
- when a specific **commit is related to more than one tag/type, we separate those components with "/"**
- more than one tag: [APP/ML_MODEL] fix: ...commit message...
- more than one type: [APP] fix/refactor: ...commit message...
- mixed: [APP/CRAWLER] fix/refactor: ...commit message...

