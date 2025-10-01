# Claude Code workflows: Spec-first development and proven approaches

The most successful developers using Claude Code v2 (released September 29, 2025) follow structured workflows that **design specifications before implementation**—exactly what you've heard about. This research compiled concrete examples, step-by-step guides, and real-world results from developers actively using these approaches in production.

## The dominant pattern: Spec-first development works

Research across multiple sources confirms that **1 iteration with a structured spec equals 8 iterations without one**. The spec-first approach you heard about has become the de facto standard, with multiple production-ready tools and frameworks now available as NPM packages and GitHub repositories.

### Why this approach dominates

Claude Code v2's official documentation explicitly recommends the **"Research → Plan → Implement → Commit"** workflow as crucial for complex tasks. Anthropic's engineering team states: "Steps #1-#2 are crucial—without them, Claude tends to jump straight to coding a solution. While sometimes that's what you want, asking Claude to research and plan first significantly improves performance for problems requiring deeper thinking upfront."

The spec-first methodology transforms this recommendation into a systematic process with persistent documentation, phase gates, and automated validation—preventing Claude from going off-track even in 20+ minute autonomous sessions.

## Concrete workflow #1: Harper Reed's production system

**Developer**: Harper Reed (former CTO, experienced developer who taught classes on codegen)  
**Results**: Built a complete BASIC interpreter in C in ~1 hour; typical projects 30-45 minutes regardless of complexity or language  
**GitHub**: github.com/harperreed/basic

### The 4-step process

**Step 1: Generate comprehensive specification**

Use a reasoning model (o1-pro, o3, or GPT-4o) to create a detailed spec document. Save as `spec.md` in project root.

```markdown
# Project: [Name]

## Overview
[High-level description, purpose, target users]

## Functional Requirements
- Feature 1: [Description]
- Feature 2: [Description]

## Non-Functional Requirements
- Architecture: [Decisions]
- Security: [Requirements]
- Performance: [Targets]

## Dependencies
- [Library]: [Usage guidance]

## Success Criteria
[Measurable outcomes]
```

**Step 2: Generate numbered prompt plan**

Have the reasoning model break the spec into a numbered list of implementation steps. Save as `prompt_plan.md`.

**Step 3: Execute with Claude Code using master prompt**

Start Claude Code and provide this master prompt:

```
1. Open @prompt_plan.md and identify any prompts not marked as completed.
2. For each incomplete prompt:
   - Double-check if it's truly unfinished (if uncertain, ask for clarification)
   - If you confirm it's already done, skip it.
   - Otherwise, implement it as described.
   - Make sure the tests pass, and the program builds/runs
   - Commit the changes to your repository with a clear commit message.
   - Update @prompt_plan.md to mark this prompt as completed.
3. After you finish each prompt, pause and wait for user review or feedback.
4. Repeat with the next unfinished prompt as directed by the user.
```

**Step 4: Defensive coding with pre-commit hooks**

Install pre-commit package and configure `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: npm test
        language: system
        pass_filenames: false
        
      - id: lint
        name: Run linter
        entry: npm run lint
        language: system
        pass_filenames: false
        
      - id: typecheck
        name: Type check
        entry: npm run typecheck
        language: system
        pass_filenames: false
```

### Why this workflow succeeds

Harper Reed's key insight: **"THE ROBOTS LOVE TDD. Seriously. They eat it up. With TDD you have the robot friend build out the test, and the mock. Then your next prompt you build the mock to be real... It is the most effective counter to hallucination and LLM scope drift I have found."**

The pre-commit hooks catch Claude's eagerness to commit broken code before it hits your CI/CD pipeline, providing a fast feedback loop that dramatically improves code quality.

**Problems solved**: Built unfamiliar language projects in ~1 hour; completed plans typically 8-12 steps in 30-45 minutes regardless of complexity; prevented scope drift and hallucination through TDD enforcement.

## Concrete workflow #2: Production-ready NPM package

**Tool**: Pimzino's claude-code-spec-workflow  
**Status**: Production-ready NPM package, actively used by developers  
**Installation**: `npm install -g @pimzino/claude-code-spec-workflow`  
**GitHub**: github.com/Pimzino/claude-code-spec-workflow

### Automated 4-phase workflow

This tool creates slash commands that guide Claude through a structured specification process automatically.

**Phase 1: Requirements generation**

```bash
# Create new feature specification
/spec-create user-authentication "Secure login system"

# Generate requirements document using EARS format
/spec-requirements
```

Claude generates a structured requirements document with testable WHEN/IF/THEN statements:

```markdown
## User Authentication Requirements

WHEN a user submits the login form with valid credentials
THEN the system shall authenticate the user and redirect to dashboard

IF the user enters invalid credentials
THEN the system shall display an error message "Invalid username or password"
AND the system shall not grant access

WHEN a user remains inactive for 30 minutes
THEN the system shall automatically log out the user
AND clear all session data
```

**Phase 2: Design creation**

```bash
/spec-design
```

Claude creates a technical architecture document including:
- System architecture diagrams (Mermaid format)
- Component specifications
- API endpoint definitions
- Data models
- Technology stack decisions
- Security considerations

**Phase 3: Task breakdown**

```bash
/spec-tasks
```

Claude generates atomic, testable tasks with TDD focus:

```markdown
## Phase 1: Foundation (Est: 2-3 hours)
- [ ] Task 1.1: Setup project structure
  - Files: package.json, tsconfig.json
  - Success: `npm install` completes without errors
  
- [ ] Task 1.2: Configure database
  - Files: db/schema.sql, db/migrations/
  - Success: Database migrations run successfully

## Phase 2: Core Features (Est: 4-5 hours)
- [ ] Task 2.1: Implement user registration
  - Files: services/UserService.ts, routes/auth.ts
  - Test: User can register with valid email/password
  - Success: Unit tests pass
```

**Phase 4: Execution**

```bash
# Execute specific tasks
/spec-execute 1

# Check progress
/spec-status

# List all specifications
/spec-list
```

Output from `/spec-status`:

```
📊 Specification Status Report
Active Specifications:
- [ACTIVE] 001-basic-todo-app

Phase Completion Status:
✅ Requirements Phase (Approved: Jul 21 12:01)
✅ Design Phase (Approved: Jul 21 12:14)
✅ Tasks Phase (Approved: Jul 21 12:17)
🚧 Implementation Phase (In Progress)

Task Completion: 30/78 (38.5%)
Time Estimate: ~48 tasks remaining, 8-10 hours
```

**Real example**: Developer created a complete asteroids game using this workflow—used `/spec-create` to generate requirements, design, and task list, then implemented successfully.

### Project structure created

```
your-project/
├── .claude/
│   ├── commands/          # Slash commands
│   ├── templates/         # Document templates
│   ├── specs/            # Generated specifications
│   │   ├── 001-feature-name/
│   │   │   ├── README.md
│   │   │   ├── requirements.md
│   │   │   ├── design.md
│   │   │   └── tasks.md
│   └── spec-config.json
└── CLAUDE.md
```

## Concrete workflow #3: Phase-gated development

**Tool**: Paolo Barbato's spec-based-claude-code  
**GitHub**: github.com/papaoloba/spec-based-claude-code  
**Unique feature**: Immutable phase gates prevent premature advancement

### Sequential phases with approval gates

This framework enforces sequential progression through requirements → design → tasks → implementation, with explicit approval required at each stage.

**Creating phase gate markers**:

```bash
# After completing requirements
/spec:approve requirements
# Creates immutable .requirements-approved file

# After completing design
/spec:approve design
# Creates .design-approved file

# After completing tasks
/spec:approve tasks
# Creates .tasks-approved file
```

These marker files prevent Claude from jumping ahead before you've reviewed and approved each phase, solving the common problem of AI agents making implementation decisions before the architecture is finalized.

### Status dashboard

The `README.md` in each spec directory acts as a real-time dashboard:

```
📊 Specification Status Report
Active Specifications:
- [ACTIVE] 001-basic-todo-app

Phase Completion Status:
✅ Requirements Phase (Approved: Jul 21 12:01)
✅ Design Phase (Approved: Jul 21 12:14)
✅ Tasks Phase (Approved: Jul 21 12:17)
🚧 Implementation Phase (In Progress)

Task Completion: 30/78 (38.5%)
Time Estimate: ~48 tasks remaining, 8-10 hours
```

**Problems solved**: Prevents Claude from making premature architectural decisions; provides audit trail of design decisions; enables rollback to any approved phase; tracks progress across long development sessions.

## Concrete workflow #4: Interactive specification building

**Approach**: Question-driven spec generation  
**Source**: Multiple developers on goatreview.com and Medium  
**Best for**: Complex domains where you need Claude to challenge your assumptions

### The 3-phase collaborative process

**Phase 1: Specification through dialogue**

Use this prompt template to transform Claude into a technical consultant:

```
You are a specification writer. Your task is to write a detailed 
specification for [PROJECT DESCRIPTION].

Ask me questions until everything is clear before starting the writing.

Rules to follow:
- Never write code, only pseudo-code when necessary
- Use Mermaid diagrams to add understanding
- Be concise in your sentences/explanations
- Produce an implementation steps plan at the end

Once the specification is done, save it in a Markdown file.
If you loop or get lost, ask me a question so I can guide you.
```

Claude will challenge assumptions, identify edge cases, and reveal blind spots through structured questioning. This collaborative refinement continues until the specification is comprehensive.

**Phase 2: TDD-inspired task breakdown**

```
Your objective is to produce an implementation specification following 
TDD methodology from the following specification: @spec.md

Break down into atomic functionalities with:
- One functionality = One test = Verification before proceeding

Create a detailed step-by-step plan where each step is:
1. Clearly defined and testable
2. Independent from others
3. Can be validated before moving forward

Rules:
- Never anticipate implementation choices in the spec
- Focus on WHAT, not HOW
- Each step must have clear success criteria
```

**Phase 3: Test-first execution**

For each task, use this prompt pattern:

```
Your objective is to implement the test functionality: [TASK_NAME]

Rules to follow:
- Even if you have a bug, NEVER write other tests or test files
- Ask me questions instead
- Never write code comments, EVER

The task is only finished once the test passes green.
```

**Benefits**: Atomic units limit context needed per task; reduces token consumption dramatically; eliminates risk of Claude "going off the rails"; each step executable individually with dedicated prompt.

## Concrete workflow #5: Roadmap-based development

**Developer**: Zhu Liang (thegroundtruth.substack.com)  
**Results**: Completed complex tasks in single 10-20 minute autonomous sessions  
**Best for**: Existing projects with ongoing development

### Document hierarchy

```
docs/
├── ROADMAP.md           # High-level overview, development workflow
├── AD_HOC_TASKS.md     # Small enhancements/refactoring
└── REFACTORS.md        # Technical debt tracking

tasks/
├── 001-db.md           # Detailed task plans
├── 002-source-library.md
├── 003-e2e-testing.md
└── 000-sample.md       # Template for new tasks
```

### Individual task file template

```markdown
# Task 012: Post Editor UI Adjustments

## Progress Summary
**Status**: Not Started
- [ ] Step 1: Create Version Navigation Component
- [ ] Step 2: Create Compact Info Bar Component
- [ ] Step 3: Integrate Components
- [ ] Step 4: Update Routing

## Overview
[Feature description and context]

## Current State Analysis
[Existing implementation details]

## Target State
[Desired outcome with specific requirements]

## Implementation Steps

### Step 1: Create Version Navigation Component
[Detailed instructions]

**Files to create/modify:**
- `components/posts/version-navigation.tsx`

**Expected behavior:**
- Version navigation displays correctly
- Clicking versions switches content

### Step 2: Create Compact Info Bar Component
[Detailed instructions]

**Files to create/modify:**
- `components/posts/info-bar.tsx`

## Acceptance Criteria

### Functional Requirements
- [ ] Version navigation works correctly
- [ ] Info bar displays all required data
- [ ] Mobile responsive design
- [ ] Accessibility standards met

### Technical Requirements
- [ ] TypeScript types properly defined
- [ ] Unit tests for all components
- [ ] Integration tests for workflows
- [ ] Performance: renders in \u003c 100ms

## Files Involved

### New Files
- `components/posts/version-navigation.tsx`
- `components/posts/info-bar.tsx`

### Modified Files
- `app/(dashboard)/dashboard/posts/[id]/page.tsx`
- `styles/posts.css`
```

### Execution workflow

1. **Describe requirement** → Claude updates `ROADMAP.md` with high-level summary
2. **Review and adjust** → Refine the approach if needed
3. **Agent writes detailed plan** → Claude creates individual task file with complete breakdown
4. **Review plan** → Make amendments before implementation
5. **Implement** → Either step-by-step OR one-shot entire task depending on complexity

**Results**: Successfully completed tasks in 10-20 minute autonomous sessions with Claude Code (vs 5-10 minutes with Cursor but requiring more supervision).

## Claude Code v2 features for spec-first workflows

Released September 29, 2025, Claude Code v2 introduces features specifically designed to enhance spec-first development:

### Checkpointing system

**How it works**: Automatically saves code state before each change Claude makes. Access with double-tap ESC (ESC+ESC) or `/rewind` command.

**Three restore modes**:
- **Conversation only**: Rewind to a user message while keeping code changes
- **Code only**: Revert file changes while keeping the conversation
- **Both code and conversation**: Complete restoration to previous session state

**Critical for spec-first workflows**: Enables exploring alternative implementation approaches without risk. If Phase 3 implementation doesn't work, rewind to Phase 2 design and try a different approach while preserving your conversation context.

### Plan Mode for specification review

**Activation**: Press Shift+Tab twice to enter read-only planning mode

**Usage in spec-first workflows**:

```bash
# Start session in plan mode
claude --permission-mode plan

# Or during session, use Shift+Tab twice
# Then provide planning prompt:
```

Example prompt:
```
I need to refactor our authentication system to use OAuth2. 
First, analyze the current implementation, identify all affected 
components, and create a detailed migration plan with risk assessment.
```

Claude analyzes thoroughly without making any changes, creating a comprehensive plan you can review before switching to implementation mode.

**Benefits**: No risk of accidental changes during planning; comprehensive system understanding before coding; creates audit trail of architectural decisions; enables "higher-order prompts" (prompts operating on prompts).

### Native VS Code extension (Beta)

**Features**: Dedicated sidebar panel with inline diffs showing changes in real-time; keyboard shortcuts (Alt+Cmd+K on Mac, Alt+Ctrl+K on Windows/Linux) to push selected code into prompts.

**Best for**: Developers who prefer IDE integration while maintaining spec-first workflow discipline.

**Current limitations**: Lacks MCP server configuration and subagents setup in beta; these features remain CLI-exclusive.

### Subagents for parallel specification work

Create specialized sub-agents for different aspects of specification:

```bash
/subagents new requirements-analyzer
# Claude generates specialized prompt for requirements analysis

/subagents new architecture-designer
# Claude generates specialized prompt for architecture design

/subagents new test-generator
# Claude generates specialized prompt for test creation
```

**Usage pattern**:
```
Use the requirements-analyzer subagent to review the spec and identify 
gaps, then use the architecture-designer subagent to propose three 
different architectural approaches, and finally have the test-generator 
create comprehensive test suites for the winning approach.
```

**Benefits**: Separate context windows prevent context pollution; task-specific prompts improve quality; automatic delegation based on task description; enables parallel specification work.

## Real-world results from spec-first workflows

### Anthropic internal teams (10+ teams documented)

**Growth Marketing Team**:
- **Problem**: Manual ad creation taking 2+ hours for hundreds of variations
- **Spec-first approach**: Created workflow spec with two specialized sub-agents (headlines: 30 char limit, descriptions: 90 char limit)
- **Results**: 87.5% reduction in time (2 hours → 15 minutes); 10x increase in creative output; built Figma plugin generating 100+ ad variations in half a second

**Product Design Team**:
- **Problem**: Complex state management changes requiring engineering resources
- **Spec-first approach**: Paste mockup images, have Claude generate functional spec, review before implementation
- **Results**: 2-3x faster execution; complex projects from weeks to hours (Google Analytics messaging: 1 week → two 30-minute calls); designers directly implementing state management changes

**Security Engineering Team**:
- **Problem**: Infrastructure debugging taking 10-15 minutes; code often shipped without tests
- **Spec-first approach**: Shifted to Claude-guided TDD with specification before implementation
- **Results**: 50% reduction in debugging time (10-15 min → ~5 min); more reliable, testable code; team members productive within days instead of weeks

### Solo developer project rescue

**Developer**: R. Brunell (anonymous solo developer)  
**Project**: Legacy system rebuild for specialty retailer  
**Initial status**: 3 months into 6-week project, completely overwhelmed

**Transformation metrics (4-week averages, before → after)**:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Story points completed/week | 14 | 37 | **+164%** |
| Bugs resolved/week | 6 | 15 | +150% |
| Time per bug (hours) | 3.7 | 1.5 | -60% |
| PR rejection rate | 23% | 8% | -65% |
| Estimation accuracy | ±65% | ±15% | +50% |

**Timeline impact**:
- Original estimate: 6 months
- Revised (pre-Claude): 9 months (due to delays)
- **Actual completion: 5 months** (1 month ahead of original!)

**Key breakthrough**: "Within four days of implementing the Claude Code workflow, I completed what had been planned as three weeks of work"

**Workflow used**: Implemented spec-first methodology with architecture analysis, bottleneck identification, and TDD enforcement through pre-commit hooks.

### Thoughtworks experiment: CodeConcise language support

**Project**: Adding programming language support to CodeConcise (AI-enabled code discovery tool)  
**Typical timeline**: 2-4 weeks with pair of developers

**SUCCESS: Python support**
- **Prompt**: "Need guidance on changes to implement Python support in CodeConcise"
- **Result**: Claude accurately identified ALL necessary changes after inspecting other ingestion tools
- **Timeline**: SME + Claude Code took **half a day vs typical 2-4 weeks (97% time reduction!)**

**FAILURE: JavaScript support**
- Attempted 3 times with different approaches (ANTLR grammar, treesitter, regex)
- All three attempts failed completely
- Claude referenced libraries that don't exist

**Key insight**: "Claude Code saved us 97% of the work on the first try. Then it failed utterly." Success depends on well-structured code, standard libraries, and Claude's training data coverage.

### Puzzmo: 6 weeks of transformation

**Developer**: Orta Therox (experienced engineer, "bizdev" role)  
**Duration**: 6 weeks intensive use

**Major migrations completed solo** (partial list):
- Converting hundreds of React Native components to React
- Replaced 3 non-trivial RedwoodJS systems
- Converted from Jest to Vitest
- Created front-end testing strategies for React
- Migrated significant code from inline styles to stylex
- Converted all animations to unified techniques
- Built iPad support for Puzzmo app
- Migrated all production projects to Node 22

**Key point**: "None of these projects are the 'actual work' which I need to do on a day to day basis... These are literally side-projects which I did on my own while working on something else."

**New game development**: Created "prototypes" monorepo enabling game designer to go from idea to running on puzzmo.com in couple of hours. Missing Link game released using this technique became a hit.

**Assessment**: Claude Code functions as "post-junior" engineer—"can ship a well-defined product feature" with "lots of experience and energy" but "doesn't do good job remembering" and needs supervision.

## Language and framework agnostic approaches

All documented spec-first workflows are **intentionally language-agnostic** by design:

### Harper Reed's approach
Successfully used for C (BASIC interpreter), Python (with Ruff), JavaScript (with Biome), and Rust (with Clippy). The `spec.md` and `prompt_plan.md` format works identically across languages.

### Pimzino and Paolo Barbato frameworks
Generate requirements, design, and tasks independently of implementation language. The specification documents are pure markdown with Mermaid diagrams—no language-specific assumptions.

### Task file templates
Zhu Liang's ROADMAP.md approach successfully used for TypeScript/React projects, but the template structure works for any stack. The task breakdown focuses on "what" not "how," making it language-agnostic.

### CLAUDE.md context file
Universal approach that works with any language, library, or framework. Example entries:

```markdown
# Project: Multi-Language Service

## Stack
- Backend: Go with Gin framework
- Frontend: React with TypeScript
- Database: PostgreSQL with Prisma ORM
- Testing: Go: testify, React: Jest + React Testing Library

## Coding Standards
- Go: Follow Effective Go guidelines, use golangci-lint
- TypeScript: Strict mode, no `any` types
- All functions: JSDoc/GoDoc comments
- Write unit tests for all business logic

## Dependencies Usage
- Gin: RESTful routing, middleware for auth
- Prisma: Database access, never raw SQL
- React Query: Server state management
```

This format adapts to any technology stack—just specify your particular choices and guidelines.

## Step-by-step guide: Complete spec-first workflow

Here's a comprehensive walkthrough combining the best practices from all researched approaches:

### Phase 0: Setup (one-time)

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Install spec workflow tool (choose one)
npm install -g @pimzino/claude-code-spec-workflow
# OR clone Paolo's framework
# OR use Harper Reed's approach (no installation needed)

# Install pre-commit hooks
pip install pre-commit
# OR: npm install -g pre-commit (if using npm)
```

### Phase 1: Generate specification (5-15 minutes)

**Option A: Using reasoning model**

Use Claude.ai with Sonnet 4.5 (or o1-pro/o3) to generate comprehensive spec:

```
Create a detailed specification for [YOUR PROJECT DESCRIPTION].

Include:
- Overview and purpose
- Functional requirements (use EARS format: WHEN/IF/THEN)
- Non-functional requirements (architecture, security, performance)
- Technology stack with specific libraries
- Data models
- Success criteria

Use Mermaid diagrams for architecture visualization.
```

Save output as `spec.md` in project root.

**Option B: Using Claude Code interactively**

```bash
claude

# In Claude Code session:
You are a specification writer. Ask me questions about my project 
until everything is clear, then write a comprehensive specification 
following EARS format for requirements.

Project: [YOUR DESCRIPTION]
```

### Phase 2: Generate prompt plan (5 minutes)

If using Harper Reed's approach:

```
Based on @spec.md, generate a numbered list of implementation prompts. 
Each prompt should be:
- Self-contained and clear
- Focused on a single feature or component
- Include testing requirements
- Small enough to complete in one session

Format as markdown with checkboxes. Save as prompt_plan.md.
```

If using Pimzino's tool:

```bash
/spec-create [feature-name] "[brief description]"
/spec-requirements
/spec-design
/spec-tasks
```

### Phase 3: Review and approve (10-30 minutes)

**Critical step**: Read the generated specifications thoroughly. Check for:
- Missing requirements or edge cases
- Unclear or ambiguous language
- Architecture decisions that don't match your constraints
- Technology choices that conflict with your stack
- Unrealistic timelines or complexity estimates

Make revisions until the specification is accurate and complete. If using Paolo's framework, explicitly approve:

```bash
/spec:approve requirements
/spec:approve design
/spec:approve tasks
```

### Phase 4: Configure project context (10 minutes)

Create or update `CLAUDE.md` in project root:

```markdown
# Project: [Name]

## Overview
[Brief description from spec]

## Development Commands
- Build: `npm run build`
- Test: `npm test`
- Dev: `npm run dev`
- Lint: `npm run lint`

## Coding Standards
- [Language]: [Specific guidelines]
- Testing: TDD approach, write tests before implementation
- Documentation: [JSDoc/GoDoc/etc] for all public functions
- Error handling: [Specific patterns]

## Architecture
[Key architectural decisions from spec]

## Test-Driven Development
ALWAYS write tests before implementation:
1. Write failing test
2. Implement minimal code to pass
3. Refactor while keeping tests green
4. Commit

## Anti-patterns (DO NOT)
- [List specific things to avoid based on your standards]

## Current Specification
See @spec.md for complete specification
See @prompt_plan.md (or tasks/XXX.md) for implementation plan
```

### Phase 5: Configure pre-commit hooks (5 minutes)

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: Run tests
        entry: npm test  # OR: go test ./... OR: pytest OR: cargo test
        language: system
        pass_filenames: false
        
      - id: lint
        name: Run linter
        entry: npm run lint  # OR: golangci-lint run OR: ruff check
        language: system
        pass_filenames: false
        
      - id: typecheck
        name: Type check
        entry: npm run typecheck  # OR: mypy . OR: go vet
        language: system
        pass_filenames: false
```

Install hooks:
```bash
pre-commit install
```

### Phase 6: Execute implementation (main development loop)

**Start Claude Code in Plan Mode** for first task:

```bash
claude --permission-mode plan
```

Provide the master prompt (Harper Reed style):

```
1. Open @prompt_plan.md and identify any prompts not marked as completed.
2. For each incomplete prompt:
   - Double-check if it's truly unfinished
   - If confirmed, implement it as described
   - Write tests FIRST using TDD approach (see @CLAUDE.md)
   - Make sure all tests pass and program builds/runs
   - Commit changes with descriptive message
   - Update @prompt_plan.md to mark prompt as completed
3. After each prompt, pause for my review
4. Repeat with next unfinished prompt when I confirm
```

**OR** if using Pimzino's tool:

```bash
/spec-execute 1
# Claude implements Task 1 following TDD

# Check progress
/spec-status

# Continue with next task
/spec-execute 2
```

**For each task**:
1. Claude enters Plan Mode, analyzes task, proposes approach
2. You review the plan—if good, switch to normal mode (Shift+Tab)
3. Claude implements tests first
4. Claude implements code to pass tests
5. Pre-commit hooks validate before commit
6. If hooks fail, Claude fixes issues
7. Task marked complete, move to next

### Phase 7: Checkpoint and review (after each major task)

```bash
# Create checkpoint manually
git commit -m "Completed Task X: [Description]"
git tag checkpoint-task-X

# OR use Claude Code's checkpoint system
# ESC+ESC to access checkpoint menu
```

Review Claude's work:
- Run the application manually
- Check test coverage
- Review code for unnecessary complexity
- Verify it matches the specification

If something's wrong, use checkpoints to rollback:
```bash
# Using Claude Code checkpoints
/rewind
# Choose: Code only, Conversation only, or Both

# Using Git
git reset --hard checkpoint-task-X
```

### Phase 8: Iterate and refine (as needed)

If Claude goes off-track:
1. Press ESC to interrupt
2. Review what went wrong
3. Update CLAUDE.md with clarification
4. Rewind to last good checkpoint
5. Provide more specific guidance

If the specification needs adjustment:
1. Update spec.md with changes
2. Regenerate affected tasks
3. Use Claude to update implementation plan
4. Continue from current point

### Phase 9: Final validation (before deployment)

```bash
# Have Claude perform comprehensive review
claude

Review the completed implementation against @spec.md:
1. Verify all functional requirements met
2. Check non-functional requirements (performance, security, etc.)
3. Run full test suite and report coverage
4. Identify any technical debt or areas for improvement
5. Generate deployment checklist
```

## Common mistakes and how to avoid them

### Mistake #1: Skipping the planning phase

**Problem**: Jumping straight to code without specification  
**Impact**: Claude makes wrong assumptions, implements incorrect architecture, requires extensive rework  
**Solution**: Always use Plan Mode (Shift+Tab twice) for complex tasks. Force yourself to write/review spec before any implementation.

### Mistake #2: Specifications too vague

**Problem**: "Build a todo app" without details  
**Impact**: Claude fills gaps with assumptions that don't match your needs  
**Solution**: Use EARS format (WHEN/IF/THEN) for testable requirements. Include specific technology choices, performance targets, and success criteria.

### Mistake #3: Not breaking down large tasks

**Problem**: Trying to implement entire features in one session  
**Example**: "Implement authentication with OAuth2, email verification, password reset, 2FA, and session management"  
**Impact**: Context limits hit, Claude loses focus, token costs explode  
**Solution**: Break into atomic tasks. Example: Task 1 = Basic OAuth2, Task 2 = Email verification, Task 3 = Password reset, etc.

### Mistake #4: Ignoring test-driven development

**Problem**: Writing tests after implementation (or not at all)  
**Impact**: Claude hallucinates functionality, code doesn't actually work, bugs multiply  
**Solution**: Enforce TDD in CLAUDE.md. Use pre-commit hooks to prevent commits without tests. Harper Reed: "THE ROBOTS LOVE TDD...most effective counter to hallucination"

### Mistake #5: Not using CLAUDE.md for context

**Problem**: Treating each session as fresh start  
**Impact**: Claude forgets previous decisions, repeats mistakes, inconsistent code style  
**Solution**: Maintain comprehensive CLAUDE.md with coding standards, architectural decisions, common patterns. Update it when Claude makes mistakes "so it remembers for next time."

### Mistake #6: Over-complex specifications

**Problem**: 50-page specification documents with excessive detail  
**Impact**: Token limits exhausted just reading spec, Claude overwhelmed, high costs  
**Solution**: Keep specs concise but complete. Focus on WHAT (requirements) not HOW (implementation). Let Claude figure out implementation details within architectural constraints.

### Mistake #7: Working without version control

**Problem**: No Git commits, relying only on Claude Code checkpoints  
**Impact**: No backup if checkpoints expire (30 days), can't share with team, no audit trail  
**Solution**: Use checkpoints + Git together. Commit after each major task. Create branches for features. Checkpoints are "local undo," Git is "permanent history."

### Mistake #8: Not using pre-commit hooks

**Problem**: Claude commits broken code, CI/CD fails, debugging cycle lengthens  
**Impact**: Time wasted on broken builds, regression bugs slip through  
**Solution**: Configure pre-commit hooks for tests, linting, type checking. Harper Reed: "Prevents 'the robot wants to commit' problem—Claude commits broken code, pre-commit hooks catch issues."

## Best practices synthesis

### Context is everything

**Multiple sources emphasize**: "PROVIDE CONTEXT, ORGANIZE CONTEXT, ITERATE ON CONTEXT. I cannot stress this enough." (Preset.io)

Create hierarchical CLAUDE.md files:
- **Project root**: Shared team instructions, architecture, coding standards
- **Subdirectories**: Module-specific instructions (e.g., frontend/, backend/, tests/)
- **~/.claude/**: Personal preferences across all projects

Claude prioritizes the most specific/nested when relevant.

### Test-driven development is non-negotiable

**Universal recommendation across all sources**: TDD dramatically improves code quality with AI assistance.

Harper Reed: "The robots LOVE TDD. Seriously. They eat it up."  
Security Engineering team: Transformed from "give up on tests" to reliable, testable code  
Multiple developers: "Way way higher test coverage than ever before"

### Small, incremental changes win

Break features into atomic tasks that can be:
- Completed in one session (10-20 minutes)
- Tested independently
- Committed separately
- Rolled back without affecting other work

DoltHub: "The smaller and more isolated the problem, the better"

### Use Plan Mode for complex decisions

**Pattern from successful teams**: Plan Mode (Shift+Tab twice) for architecture decisions, normal mode for implementation.

Benefits:
- No risk of accidental changes during planning
- More thorough analysis before coding
- Creates audit trail of decisions
- Enables "what if" exploration

### Checkpoints enable ambitious work

Claude Code v2's checkpoint system (ESC+ESC or `/rewind`) transforms risk management:
- Try aggressive refactors with confidence
- Explore alternative implementations
- Recover from mistakes instantly
- Persists for 30 days across sessions

**Use pattern**: Before risky changes, explicitly tell Claude "this is an experiment, I may rewind"—encourages bolder attempts.

### Active collaboration beats passive observation

**Anthropic guidance**: "While auto-accept mode lets Claude work autonomously, you'll typically get better results by being an active collaborator and guiding Claude's approach"

Best performing teams:
- Interrupt with ESC when Claude goes wrong direction
- Provide course corrections mid-execution
- Review plans before approval
- Verify output at checkpoints

### Multiple parallel instances for complex projects

**Advanced pattern** from Puzzmo, Anthropic teams, Christian Houmann:

```bash
# Terminal 1: Frontend
cd project/frontend && claude

# Terminal 2: Backend  
cd project/backend && claude

# Terminal 3: Testing
cd project && claude
```

**Benefits**: Parallel development, separate contexts, different permission modes, specialized subagents per domain.

**Tip**: Use Git worktrees for true parallelization on same codebase.

## Claude Code v2 compatibility notes

All documented workflows are **fully compatible with Claude Code v2** (released September 29, 2025). In fact, v2's new features specifically enhance spec-first development:

### Features that improve spec-first workflows

**Checkpointing**: Enables experimentation with different implementations of the same spec—try approach A, rewind, try approach B, compare results.

**Subagents**: Create specialized agents for requirements analysis, architecture design, implementation, testing—each with focused context and prompts.

**Hooks**: Automatically trigger actions at specific points:
- PreEdit: Check if task has approved spec before allowing implementation
- PostEdit: Run tests, update task completion status
- PreCommit: Verify all acceptance criteria met

**VS Code extension (Beta)**: Inline diffs let you review spec-generated code alongside specification documents in split view.

### Using v2 features in spec-first workflow

Example hook configuration (`.claude/hooks.mjs`):

```javascript
export async function preEdit({ filePath, oldContent, newContent }) {
  // Check if implementation has approved spec
  const taskId = process.env.CURRENT_TASK_ID;
  if (taskId) {
    const specPath = `.claude/specs/${taskId}/.design-approved`;
    if (!fs.existsSync(specPath)) {
      throw new Error(`❌ Task ${taskId} design not approved. Review spec first.`);
    }
  }
  return { proceed: true };
}

export async function postEdit({ filePath, success }) {
  if (!success) return;
  
  // Run tests after implementation
  if (filePath.match(/\.(ts|js|go|rs)$/)) {
    execSync(`npm test ${filePath}`, { stdio: 'inherit' });
  }
  
  // Update task status
  const taskId = process.env.CURRENT_TASK_ID;
  if (taskId) {
    updateTaskProgress(taskId, filePath);
  }
}
```

## Additional resources

### Official documentation
- Claude Code docs: docs.claude.com/en/docs/claude-code/overview
- Best practices guide: anthropic.com/engineering/claude-code-best-practices
- v2 announcement: anthropic.com/news/enabling-claude-code-to-work-more-autonomously

### Production-ready tools
- Pimzino's NPM package: npmjs.com/package/@pimzino/claude-code-spec-workflow
- Paolo Barbato's framework: github.com/papaoloba/spec-based-claude-code
- Harper Reed's BASIC interpreter example: github.com/harperreed/basic
- TDD Guard enforcement: github.com/nizos/tdd-guard
- Awesome Claude Code collection: github.com/hesreallyhim/awesome-claude-code

### Developer blogs with step-by-step guides
- Harper Reed on spec-driven workflow: harper.blog/2025/05/08/basic-claude-code/
- Builder.io production usage: builder.io/blog/claude-code
- Zhu Liang's roadmap approach: thegroundtruth.substack.com/p/my-claude-code-workflow
- Sid Bharath's complete tutorial: siddharthbharath.com (building finance tracker)
- Preset.io on large repo adoption: preset.io/blog/adopting-claude-code

### Case studies with metrics
- Anthropic internal teams (10+ teams): anthropic.com/news/how-anthropic-teams-use-claude-code
- Solo developer project rescue (164% productivity increase): medium.com/@raymond_44620
- Puzzmo transformation (6 weeks): blog.puzzmo.com/posts/2025/07/30/six-weeks-of-claude-code/
- Thoughtworks experiment (97% time reduction): thoughtworks.com/insights/blog/generative-ai/claude-code-codeconcise-experiment
- Building Claude Code itself: newsletter.pragmaticengineer.com/p/how-claude-code-is-built

### Community resources
- ClaudeLog knowledge base: claudelog.com
- Product Hunt discussions: producthunt.com/p/cursor (Cursor vs Claude Code debates)
- Hacker News threads: search "Claude Code" on news.ycombinator.com
- Reddit communities: r/ClaudeAI, r/LocalLLaMA (discussions on workflows)

## Summary: The spec-first advantage

The research conclusively shows that **structured specification before implementation** is not just a best practice—it's the defining characteristic of successful Claude Code projects. The data speaks clearly:

**Quality improvements**: 1 iteration with structured spec = 8 iterations without spec (AI Native Dev research)  
**Code rework reduction**: 30% less rework vs unstructured approaches (Product Hunt data)  
**Time savings**: 97% reduction in development time for well-structured tasks (Thoughtworks)  
**Productivity gains**: 164% increase in story points, 60% reduction in debugging time (solo developer metrics)  
**Scale improvements**: 10x creative output, years of tech debt in 6 weeks (Anthropic teams, Puzzmo)

The spec-first methodology you heard about is real, production-proven, and now available as installable tools. Harper Reed's workflow, Pimzino's NPM package, and Paolo Barbato's framework provide concrete implementations you can use today—compatible with Claude Code v2 and working across any programming language, library, or framework.

The secret isn't just having Claude Code—it's **designing specifications that Claude uses to implement and test changes systematically**, with phase gates, TDD enforcement, and checkpoints ensuring quality throughout the process. That's exactly what these workflows deliver.