# Chapter 6 - Home Assignment Requirements

**Source:** AI Agents with Model Context Protocol by Dr. Yoram Segal
**Date:** December 9, 2025

## 1. Assignment Goal

Implement a player agent for an even/odd league game. The agent risk is contained only in your environment. Coordination with other students is highly recommended to ensure protocol compliance.

**CRITICAL:** Use exactly the protocol defined in this document. Otherwise, your agent will not be able to communicate with others.

## 2. Mandatory Tasks

### Task 1: Player Agent Implementation

Implement an MCP server listening on localhost. The server **MUST** support the following tools:

1. **`handle_game_invitation`**
   - Receive game invitation
   - Return `GAME_JOIN_ACK`

2. **`parity_choose`**
   - Choose "even" or "odd"
   - Return `RESPONSE_PARITY_CHOOSE`

3. **`notify_match_result`**
   - Receive game result
   - Update internal state

### Task 2: League Registration

The agent **MUST** send a registration request to the league manager including:

- **Unique display name** (your name or nickname)
- **Agent version**
- **Endpoint address** of the server

### Task 3: Self-Testing

Before submission, test your agent:

1. Run a local league with **4 players**
2. Verify the agent **responds to all types of messages**
3. Verify **JSON structure conforms to the protocol**

## 3. Technical Requirements

### 3.1 Programming Language

You may choose any programming language. The main requirement:

- **Implements an HTTP server**
- **Responds to POST requests** at the `/mcp` path
- **Returns JSON** in JSON-RPC 2.0 format

### 3.2 Response Timeouts

- **`GAME_JOIN_ACK`** - within 5 seconds
- **`CHOOSE_PARITY_RESPONSE`** - within 30 seconds
- **Any other response** - within 10 seconds

### 3.3 Stability

The agent **MUST**:

- Operate without crashes
- Handle input errors
- Not stop operating mid-league

## 4. Work Process

### Stage 1: Local Development

1. Implement the agent
2. Test locally with your code
3. Fix bugs

### Stage 2: Private League

1. Run a local league with **4 copies of your agent**
2. Verify all communication works
3. Improve strategy (optional)

### Stage 3: Compatibility Testing with Other Students

1. Coordinate with another student to exchange agents
2. Verify agents communicate properly between them
3. Verify JSON structure conforms to the protocol

### Stage 4: Class League (Future)

**IMPORTANT NOTE:**

In the future, you may be required to:

- Create new games (not just even/odd)
- Compete in a class league as part of the course's final project

This topic is not yet finalized. You should build your agent in a way that allows for **future extensibility**.

## 5. Submission Requirements

### 5.1 Files to Submit

1. **Agent source code**
2. **README file** with running instructions
3. **Detailed report** including:
   - Full description of architecture and implementation
   - Description of chosen strategy and reasons for choice
   - Challenges encountered and solutions found
   - Documentation of development and testing process
   - Conclusions from the assignment and recommendations for improvement

### 5.2 Submission Format

Submit a link to a public or private repository as usual, or submit via the regular submission procedure used in previous assignments.

## 6. Evaluation Criteria

Beyond regular requirements, the following criteria will be evaluated:

| Criterion | Description |
|-----------|-------------|
| **Basic Functionality** | Agent works, responds to messages, plays games |
| **Protocol Compliance** | JSON structure exactly conforms to the protocol |
| **Stability** | Agent is stable, doesn't crash, handles errors |
| **Code Quality** | Clean, documented, organized code |
| **Documentation** | Clear running instructions, detailed description |
| **Strategy** | Implementing an interesting strategy (not just random) |

## 7. Mandatory Constraints

### What the System MUST DO:

- Implement exactly 3 required MCP tools: `handle_game_invitation`, `parity_choose`, `notify_match_result`
- Listen on localhost via HTTP server
- Accept POST requests at `/mcp` endpoint
- Return responses in JSON-RPC 2.0 format
- Register with league manager providing name, version, and endpoint
- Respond within specified timeouts (5s, 30s, 10s)
- Handle errors gracefully without crashing
- Operate continuously throughout the league
- Conform to the protocol defined in Chapters 9, 10, 11
- Function as defined in Chapter 8

### What the System MUST NOT DO:

- Must NOT deviate from the protocol specification
- Must NOT crash during operation
- Must NOT stop responding mid-league
- Must NOT exceed response timeouts

## 8. Frequently Asked Questions

### Q: Can I use external libraries?
**A:** Yes. You can use any library you want. Make sure to provide installation instructions.

### Q: Must I use Python?
**A:** No. Use any language that suits you. The main thing is that the agent meets the protocol requirements.

### Q: What happens if my agent crashes during the league?
**A:** The agent will suffer a technical loss in the current game. If it doesn't return to operation - it exits the league.

### Q: Can I update the agent after submission?
**A:** No. The final submission. Check well before you submit.

### Q: How do I know my ranking?
**A:** The ranking table will be published after each round. You will be able to see your agent's position.

## 9. Summary

1. Implement a player agent that conforms to the protocol
2. Test locally before submission
3. Submit the code and report
4. Your agent will play in the class league

## 10. Additional Notes

- For questions and clarifications, turn to Dr. Yoram Segal
- It is recommended to read the book "AI Agents with MCP" [1]
- For additional details on the MCP protocol, see the official documentation [2]
- The assignment is based on Chapter 9 (league data protocol), Chapter 10 (MCP tools architecture), Chapter 11 (project structure), and Chapter 8 (running the league system)

---

**Good luck!**
