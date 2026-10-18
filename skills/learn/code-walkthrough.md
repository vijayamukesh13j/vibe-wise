# Code walkthroughs: what it does AND how it's built

Design reasoning explains *what* the system should do and *why*. Learners also need
to see *how* the code actually implements that design, especially in an existing
repo full of code they didn't write. A design they agreed to is not understood
until they can find it in the code and read it.

Use a **Code walkthrough** when:

- A design topic is confirmed (or skipped) and code for it already exists in the repo.
- You just implemented something (fold it into the Implementation report).
- The learner says they don't understand some code, or asks "how does this work?"
- Profile `Code walkthroughs: Always` (default): do it for every topic that has code.
  `On request`: only when asked. Respect the profile setting.

## How to walk through code

Go from the outside in: entry point, then data flow, then details.

1. **Where it lives.** Name the files and functions involved as clickable links,
   with one line on each file's job. Show how they connect (who calls whom) in a
   small text diagram when more than two pieces are involved.
2. **Real excerpts, small.** Quote the actual code from the repo, 5–25 lines at a
   time, with file and line links. Never paraphrase code into pseudocode and call
   it the implementation. Skip boilerplate; show the lines that carry the logic.
3. **Line-by-line where it's unfamiliar.** Under each excerpt, explain what the
   important lines do in plain language. Explain syntax, language features, library
   APIs, and framework patterns the learner may not know (for example TypeScript
   generics or union types, `useState`, `useCallback`, `useMemo`, `.map`/`.filter`,
   spread `...`, optional chaining `?.`, `async`/`await`, browser APIs). Match
   depth to the profile: Beginner gets every new construct explained; Intermediate
   gets the non-obvious parts; Advanced gets only surprises and tradeoffs.
4. **Trace one concrete example.** Follow one real input through the code
   step by step. Example: "You rate a problem 3. `logRevision` runs, then
   `calculateNextRevisionDate(3, '2026-10-18')`, which looks up 7 days and
   returns `'2026-10-25'`." Concrete values beat abstract descriptions.
5. **Connect back to the design.** Say which lines implement which design decision
   the learner made, and point out anything the code does that the design didn't
   mention (validation, edge cases, legacy cleanup). Flag code that looks wrong or
   fragile; don't pretend it's fine.

Split big topics into several short walkthroughs (one file or flow per reply) rather
than one wall of code. Check whether the learner wants to go deeper before moving on;
don't dump every file at once.

## Keep the learner reasoning

A walkthrough explains; it isn't a quiz. But reading code is a skill, so after a
walkthrough you may offer one short **trace question**: "Given this code, what does
`diffInDays('2026-10-20', '2026-10-18')` return, and how would the UI label it?"
Ask it in normal chat, wait for their answer, and correct it gently with the code
as evidence. Skip the question if the learner wants to keep moving.

## Format

Use the heading `✦ Code walkthrough: <topic>` with a divider, like other callouts.
Code excerpts go in fenced code blocks with a language tag (the one place code
fences are expected), each preceded by a file link with a line range.

Record in `progress.md` under the topic: which files were walked through, constructs
explained, and trace answers that showed understanding or confusion. Code you only
explained is **Introduced**, not demonstrated understanding.
