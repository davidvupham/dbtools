# Project 1: Kafka CLI Management Tool

**[← Back to Module 1](./README.md)**

> **Document Version:** 1.0
> **Last Updated:** January 21, 2026
> **Status:** Production

![Project](https://img.shields.io/badge/Project-1-orange)
![Difficulty](https://img.shields.io/badge/Difficulty-Beginner-green)

## Project overview

Build a shell script that simplifies common Kafka operations. This project reinforces your understanding of Kafka CLI tools while creating a useful utility.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KAFKA CLI TOOL                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  $ ./kafka-tool.sh                                                          │
│                                                                             │
│  ╔════════════════════════════════════════════════════════════════════╗    │
│  ║                     KAFKA MANAGEMENT TOOL                           ║    │
│  ╠════════════════════════════════════════════════════════════════════╣    │
│  ║  1. List all topics                                                 ║    │
│  ║  2. Create a new topic                                              ║    │
│  ║  3. Describe a topic                                                ║    │
│  ║  4. Delete a topic                                                  ║    │
│  ║  5. Produce messages                                                ║    │
│  ║  6. Consume messages                                                ║    │
│  ║  7. List consumer groups                                            ║    │
│  ║  8. Describe consumer group                                         ║    │
│  ║  9. Reset consumer group offset                                     ║    │
│  ║  0. Exit                                                            ║    │
│  ╚════════════════════════════════════════════════════════════════════╝    │
│                                                                             │
│  Enter choice:                                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Learning objectives

By completing this project, you will:

1. Solidify your understanding of Kafka CLI commands
2. Practice shell scripting fundamentals
3. Build a reusable tool for daily Kafka operations
4. Learn to handle user input and errors gracefully

## Requirements

### Functional requirements

| Feature | Description | Priority |
|---------|-------------|----------|
| List topics | Display all topics in the cluster | Required |
| Create topic | Create with name, partitions, replication factor | Required |
| Describe topic | Show partition details and configuration | Required |
| Delete topic | Remove a topic (with confirmation) | Required |
| Produce messages | Interactive message producer | Required |
| Consume messages | Read messages with options | Required |
| List consumer groups | Show all consumer groups | Required |
| Describe consumer group | Show lag and assignment | Required |
| Reset offsets | Reset to earliest/latest | Bonus |
| Colored output | Use colors for better UX | Bonus |

### Technical requirements

- Shell script (bash)
- Works with Docker-based Kafka
- Input validation
- Error handling
- Clear user feedback

## Getting started

### Step 1: Create the project structure

```bash
mkdir -p ~/kafka-tutorial/tools
cd ~/kafka-tutorial/tools
touch kafka-tool.sh
chmod +x kafka-tool.sh
```

### Step 2: Basic script template

```bash
#!/bin/bash
#
# Kafka CLI Management Tool
# Project 1 - Kafka Engineering Course
#

# Configuration
BOOTSTRAP_SERVER="localhost:9092"
KAFKA_CONTAINER="kafka"

# Colors (optional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper function to run Kafka commands
run_kafka_cmd() {
    docker exec -it "$KAFKA_CONTAINER" "$@"
}

# Display the main menu
show_menu() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}                     ${GREEN}KAFKA MANAGEMENT TOOL${NC}                          ${BLUE}║${NC}"
    echo -e "${BLUE}╠════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC}  1. List all topics                                               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  2. Create a new topic                                            ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  3. Describe a topic                                              ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  4. Delete a topic                                                ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  5. Produce messages                                              ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  6. Consume messages                                              ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  7. List consumer groups                                          ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  8. Describe consumer group                                       ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  9. Reset consumer group offset                                   ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  0. Exit                                                          ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# TODO: Implement each function below

# Function 1: List all topics
list_topics() {
    echo -e "${YELLOW}Listing all topics...${NC}"
    # TODO: Implement this
}

# Function 2: Create a new topic
create_topic() {
    echo -e "${YELLOW}Create a new topic${NC}"
    # TODO: Implement this
}

# Function 3: Describe a topic
describe_topic() {
    echo -e "${YELLOW}Describe a topic${NC}"
    # TODO: Implement this
}

# Function 4: Delete a topic
delete_topic() {
    echo -e "${YELLOW}Delete a topic${NC}"
    # TODO: Implement this
}

# Function 5: Produce messages
produce_messages() {
    echo -e "${YELLOW}Produce messages${NC}"
    # TODO: Implement this
}

# Function 6: Consume messages
consume_messages() {
    echo -e "${YELLOW}Consume messages${NC}"
    # TODO: Implement this
}

# Function 7: List consumer groups
list_consumer_groups() {
    echo -e "${YELLOW}Listing consumer groups...${NC}"
    # TODO: Implement this
}

# Function 8: Describe consumer group
describe_consumer_group() {
    echo -e "${YELLOW}Describe consumer group${NC}"
    # TODO: Implement this
}

# Function 9: Reset consumer group offset
reset_offset() {
    echo -e "${YELLOW}Reset consumer group offset${NC}"
    # TODO: Implement this
}

# Main loop
main() {
    while true; do
        show_menu
        read -p "Enter choice [0-9]: " choice

        case $choice in
            1) list_topics ;;
            2) create_topic ;;
            3) describe_topic ;;
            4) delete_topic ;;
            5) produce_messages ;;
            6) consume_messages ;;
            7) list_consumer_groups ;;
            8) describe_consumer_group ;;
            9) reset_offset ;;
            0) echo "Goodbye!"; exit 0 ;;
            *) echo -e "${RED}Invalid option${NC}" ;;
        esac

        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run the main function
main
```

## Implementation guide

### Implementing list_topics

```bash
list_topics() {
    echo -e "${YELLOW}Listing all topics...${NC}"
    echo ""
    run_kafka_cmd kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --list
}
```

### Implementing create_topic

```bash
create_topic() {
    echo -e "${YELLOW}Create a new topic${NC}"
    echo ""

    read -p "Topic name: " topic_name
    if [[ -z "$topic_name" ]]; then
        echo -e "${RED}Error: Topic name cannot be empty${NC}"
        return 1
    fi

    read -p "Number of partitions [3]: " partitions
    partitions=${partitions:-3}

    read -p "Replication factor [1]: " replication
    replication=${replication:-1}

    echo ""
    echo "Creating topic '$topic_name' with $partitions partitions..."

    run_kafka_cmd kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --create \
        --topic "$topic_name" \
        --partitions "$partitions" \
        --replication-factor "$replication"

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Topic created successfully!${NC}"
    else
        echo -e "${RED}Failed to create topic${NC}"
    fi
}
```

### Implementing delete_topic (with confirmation)

```bash
delete_topic() {
    echo -e "${YELLOW}Delete a topic${NC}"
    echo ""

    # Show available topics
    echo "Available topics:"
    run_kafka_cmd kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --list
    echo ""

    read -p "Topic name to delete: " topic_name
    if [[ -z "$topic_name" ]]; then
        echo -e "${RED}Error: Topic name cannot be empty${NC}"
        return 1
    fi

    read -p "Are you sure you want to delete '$topic_name'? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Cancelled."
        return 0
    fi

    run_kafka_cmd kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --delete \
        --topic "$topic_name"

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}Topic deleted successfully!${NC}"
    else
        echo -e "${RED}Failed to delete topic${NC}"
    fi
}
```

### Implementing consume_messages

```bash
consume_messages() {
    echo -e "${YELLOW}Consume messages${NC}"
    echo ""

    read -p "Topic name: " topic_name
    read -p "From beginning? (y/n) [n]: " from_beginning
    read -p "Show keys? (y/n) [n]: " show_keys
    read -p "Max messages (0 for unlimited) [10]: " max_messages
    max_messages=${max_messages:-10}

    # Build command
    cmd="kafka-console-consumer --bootstrap-server $BOOTSTRAP_SERVER --topic $topic_name"

    if [[ "$from_beginning" == "y" ]]; then
        cmd="$cmd --from-beginning"
    fi

    if [[ "$show_keys" == "y" ]]; then
        cmd="$cmd --property print.key=true --property print.partition=true"
    fi

    if [[ "$max_messages" -gt 0 ]]; then
        cmd="$cmd --max-messages $max_messages"
    fi

    echo ""
    echo "Consuming messages (Ctrl+C to stop)..."
    echo ""

    run_kafka_cmd $cmd
}
```

## Testing your tool

### Test checklist

- [ ] List topics shows all topics
- [ ] Create topic works with custom partitions
- [ ] Create topic validates empty name
- [ ] Describe topic shows partition details
- [ ] Delete topic requires confirmation
- [ ] Produce messages sends to correct topic
- [ ] Consume messages shows correct output
- [ ] Consumer groups are listed correctly
- [ ] Offset reset works for earliest/latest

### Test scenarios

```bash
# Scenario 1: Full workflow
1. Create topic "test-project"
2. Produce 5 messages
3. Consume messages from beginning
4. Describe the topic
5. Delete the topic

# Scenario 2: Consumer groups
1. Create topic "group-test" with 3 partitions
2. Start consuming with group "my-group"
3. List consumer groups
4. Describe "my-group"
5. Reset offset to earliest
```

## Bonus challenges

### Challenge 1: Add topic search

Add a search function to filter topics:

```bash
search_topics() {
    read -p "Search pattern: " pattern
    run_kafka_cmd kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --list | grep -i "$pattern"
}
```

### Challenge 2: Add cluster health check

```bash
check_health() {
    echo "Checking cluster health..."

    # Check if broker is reachable
    run_kafka_cmd kafka-broker-api-versions \
        --bootstrap-server "$BOOTSTRAP_SERVER" > /dev/null 2>&1

    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✓ Kafka broker is healthy${NC}"
    else
        echo -e "${RED}✗ Cannot reach Kafka broker${NC}"
    fi

    # Check for under-replicated partitions
    under_replicated=$(run_kafka_cmd kafka-topics \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --describe --under-replicated-partitions 2>/dev/null)

    if [[ -z "$under_replicated" ]]; then
        echo -e "${GREEN}✓ No under-replicated partitions${NC}"
    else
        echo -e "${YELLOW}⚠ Under-replicated partitions found${NC}"
        echo "$under_replicated"
    fi
}
```

### Challenge 3: Add configuration export

Export topic configurations to a file:

```bash
export_topic_config() {
    read -p "Topic name: " topic_name
    read -p "Output file [topic-config.json]: " output_file
    output_file=${output_file:-topic-config.json}

    run_kafka_cmd kafka-configs \
        --bootstrap-server "$BOOTSTRAP_SERVER" \
        --entity-type topics \
        --entity-name "$topic_name" \
        --describe > "$output_file"

    echo "Configuration exported to $output_file"
}
```

## Submission criteria

Your project is complete when:

1. **All required features work** - Each menu option functions correctly
2. **Input validation** - Empty inputs and invalid values are handled
3. **Error handling** - Failures show meaningful messages
4. **User experience** - Clear prompts and feedback
5. **Code quality** - Well-organized, commented code

## Evaluation rubric

| Criteria | Points |
|----------|--------|
| All required features implemented | 40 |
| Input validation | 15 |
| Error handling | 15 |
| Code organization and comments | 15 |
| User experience (menus, feedback) | 10 |
| Bonus features | +10 |
| **Total** | **100** |

---

**Congratulations on completing Project 1!**

**Next:** [Module 2: Core Concepts →](../module_2_core_concepts/README.md)
