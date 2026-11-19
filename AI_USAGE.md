# AI Usage Documentation

## Tools Used
- Claude: project planning and walkthrough
- GitHub Copilot in VS Code: implementation, review, and documentation

## Key Prompts
1. "Walk me through how to complete this assignment and get an A..." (used to get a phase-by-phase plan)
2. "Walk me through how to do Phase 0..." (used for repo and environment setup)
3. Pasted a `git clone` authentication error and asked how to fix it (the repo name was wrong, not the login)
4. "Help me finish Contacts" (used to complete contact validation, routes, and form)
5. "Complete the next steps to finishing the assignment" (used to add the Dashboard, Job Match, and setup documentation)
6. "Check the project against every requirement before committing, fix gaps, and tell me what changed" (used for the final requirements review)

## What AI Generated
- Flask routes and server-side validation for Contacts
- Dashboard counts, application status summary, and recent application query
- Skill normalization and job match scoring, including missing-skill output
- Dashboard, Job Match, contact form, and friendly error templates/styles
- README setup instructions and this AI usage summary

## What I Modified
- My earlier project notes record that I moved the Jobs routes above the `if __name__ == "__main__"` block after discovering that routes below it were not registered.
- During the final review, Copilot corrected contact input limits to match the database schema, limited the dashboard's recent-applications query, and added a warning about the schema reset.
- Before submission, I will add any other changes I personally make after testing and reviewing the code.

## What I Learned
- I will add a short reflection after running the application and explaining the CRUD, dashboard, and Job Match features. It should describe what I understand, not just repeat AI output.

## Lessons Learned
- Keep Flask routes above the `if __name__ == "__main__"` block so every route is registered.
- Validate submitted data on the server and keep limits consistent with the database schema.
- Explain and verify AI-generated code before submitting it.
- Check the exact repo URL before assuming an authentication problem.
