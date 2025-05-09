---
sidebar_position: 42
---

# Creating and Working with Nodes in LionWeb

LionWeb provides a flexible and language-agnostic model for working with models (or trees, or ASTs: let's consider these as synonyms in this context). 

The main component is the **Node**.

When working with LionWeb nodes in Python, there are **two complementary approaches** depending on your needs:

1. **Homogeneous nodes**, using generic, universal APIs which work with all form of nodes. When choosing this approach, we may want to consider `DynamicNode`.
2. **Heterogeneous nodes**, using language-specific, statically-typed Python classes, defined for a certain LionWeb language and just that one.

## The Core Abstraction: `Node`

At the heart of LionWeb is the `Node` interface. Implementing it guarantees:

- Serialization and deserialization
- Compatibility with the LionWeb Repository
- Introspection through classifiers and features
- Tool support (e.g., editors, model processors)

By relying on this interface, LionWeb tooling can process, manipulate, and analyze any conforming node in a uniform manner.

## Option 1: Homogeneous Nodes

This approach is ideal for **generic tools** and **runtime interoperability**. The key class here is `DynamicNode`.

### When to Use

- You receive nodes from external systems or clients
- You want to handle **unknown or dynamic languages**
- You’re building **generic tools** (e.g., validators, browsers)

### How it Works

`DynamicNode` implements `Node` and stores features dynamically. You can query and manipulate the node’s structure by name.

### Example

```python
package com.example;

import io.lionweb.lioncore.java.language.*;
import io.lionweb.lioncore.java.model.ClassifierInstanceUtils;
import io.lionweb.lioncore.java.model.Node;
import io.lionweb.lioncore.java.model.impl.DynamicNode;
import io.lionweb.lioncore.java.utils.NodeTreeValidator;
import io.lionweb.lioncore.java.utils.ValidationResult;

import java.util.List;

public class HomogeneousAPIExample {

    private static Concept taskListConcept;
    private static Concept taskConcept;
    private static Property nameProperty;
    private static Containment tasksContainment;
    private static Language taskLanguage;

    {
        defineLanguage();
    }

    public static void defineLanguage() {
        // Define the 'TaskList' concept
        taskListConcept = new Concept("TaskList");
        taskListConcept.setID("TaskList-id");
        taskListConcept.setName("TaskList");
        taskListConcept.setKey("TaskList");
        taskListConcept.setAbstract(false);
        taskListConcept.setPartition(true);

        // Define the 'Task' concept
        taskConcept = new Concept("Task");
        taskConcept.setID("Task-id");
        taskConcept.setName("Task");
        taskConcept.setKey("Task");
        taskConcept.setAbstract(false);

        // Add a 'tasks' containment
        tasksContainment = new Containment()
                .setID("TasksList-tasks-id")
                .setName("tasks")
                .setKey("TasksList-tasks")
                .setMultiple(true)
                .setOptional(false)
                .setType(taskConcept);
        taskListConcept.addFeature(tasksContainment);

        // Add a 'name' property
        nameProperty = new Property();
        nameProperty.setID("task-name-id");
        nameProperty.setName("name");
        nameProperty.setKey("task-name");
        nameProperty.setType(LionCoreBuiltins.getString());
        taskConcept.addFeature(nameProperty);

        // Define the language container
        taskLanguage = new Language();
        taskLanguage.setID("task-id");
        taskLanguage.setKey("task");
        taskLanguage.setName("Task Language");
        taskLanguage.setVersion("1.0");
        taskLanguage.addElement(taskListConcept);
        taskLanguage.addElement(taskConcept);

    }

    public void useDynamicNode() {
        // Create the model
        DynamicNode errands = new DynamicNode("errands", taskListConcept);

        DynamicNode task1 = new DynamicNode("task1-id", taskConcept);
        task1.setPropertyValue(nameProperty, "My Task #1");
        errands.addChild(tasksContainment, task1);

        DynamicNode task2 = new DynamicNode("task2-id", taskConcept);
        task2.setPropertyValue(nameProperty, "My Task #2");
        errands.addChild(tasksContainment, task2);

        ValidationResult res = new NodeTreeValidator().validate(errands);
        if (!res.isSuccessful()) {
            throw new IllegalStateException("The tree is invalid: " + res);
        }

        // Access the model
        List<Node> tasks = errands.getChildren(tasksContainment);
        System.out.println("Tasks found: " + tasks.size());
        for (Node task : tasks) {
            System.out.println(" - " + task.getPropertyValue(nameProperty));
        }

        // Access the model, using ClassifierInstanceUtils
        List<? extends Node> tasksAgain = ClassifierInstanceUtils.getChildrenByContainmentName(errands, "tasks");
        System.out.println("Tasks found: " + tasksAgain.size());
        for (Node task : tasksAgain) {
            System.out.println(" - " + ClassifierInstanceUtils.getPropertyValueByName(task, "name"));
        }
    }

    public static void main(String[] args) {
        new HomogeneousAPIExample().useDynamicNode();
    }
}
```

### Evaluation

- No static typing
- No compile-time safety
- No code completion or type checking
- Work out of the box, without the need to write any code for each language

If you misspell `"name"` or access a non-existent feature, you’ll get a runtime exception.

## Option 2: Heterogeneous Nodes

This approach is recommended when building **interpreters**, **compilers**, or other tools for a **specific language**.

You define a Python class for each concept, typically:

- Implementing the `Node` interface
- Optionally extending `DynamicNode` for convenience

### But how can you define these classes?

Of course, you can do that in the good old way: writing the code yourself.

Or you can define a code generator which, given a language, produce the corresponding classes. This may also be a feature we eventually implement in LionWeb Python.

### When to Use

- You are building tooling for a specific DSL or language
- You want type-safe code with IDE support
- You require structured, validated access to features

### Example

```python
package com.example;

import io.lionweb.lioncore.java.language.*;
import io.lionweb.lioncore.java.model.impl.DynamicNode;
import io.lionweb.lioncore.java.utils.NodeTreeValidator;
import io.lionweb.lioncore.java.utils.ValidationResult;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class HeterogeneousAPIExample {

    private static Concept taskListConcept;
    private static Concept taskConcept;
    private static Property nameProperty;
    private static Containment tasksContainment;
    private static Language taskLanguage;

    {
        defineLanguage();
    }

    private class TaskList extends DynamicNode {
        TaskList() {
            super(UUID.randomUUID().toString(), taskListConcept);
        }

        void addTask(Task task) {
            addChild(tasksContainment, task);
        }

        List<Task> getTasks() {
            return getChildren(tasksContainment).stream().map(n -> (Task)n).collect(Collectors.toList());
        }
    }

    private class Task extends DynamicNode {
        Task(String name) {
            super(UUID.randomUUID().toString(), taskConcept);
            setName(name);
        }

        void setName(String name) {
            setPropertyValue(nameProperty, name);
        }

        String getName() {
            return (String) getPropertyValue(nameProperty);
        }
    }

    public static void defineLanguage() {
        // Define the 'TaskList' concept
        taskListConcept = new Concept("TaskList");
        taskListConcept.setID("TaskList-id");
        taskListConcept.setName("TaskList");
        taskListConcept.setKey("TaskList");
        taskListConcept.setAbstract(false);
        taskListConcept.setPartition(true);

        // Define the 'Task' concept
        taskConcept = new Concept("Task");
        taskConcept.setID("Task-id");
        taskConcept.setName("Task");
        taskConcept.setKey("Task");
        taskConcept.setAbstract(false);

        // Add a 'tasks' containment
        tasksContainment = new Containment()
                .setID("TasksList-tasks-id")
                .setName("tasks")
                .setKey("TasksList-tasks")
                .setMultiple(true)
                .setOptional(false)
                .setType(taskConcept);
        taskListConcept.addFeature(tasksContainment);

        // Add a 'name' property
        nameProperty = new Property();
        nameProperty.setID("task-name-id");
        nameProperty.setName("name");
        nameProperty.setKey("task-name");
        nameProperty.setType(LionCoreBuiltins.getString());
        taskConcept.addFeature(nameProperty);

        // Define the language container
        taskLanguage = new Language();
        taskLanguage.setID("task-id");
        taskLanguage.setKey("task");
        taskLanguage.setName("Task Language");
        taskLanguage.setVersion("1.0");
        taskLanguage.addElement(taskListConcept);
        taskLanguage.addElement(taskConcept);

    }

    public void useSpecificClasses() {
        // Create the model
        TaskList errands = new TaskList();

        Task task1 = new Task("My Task #1");
        errands.addTask(task1);

        Task task2 = new Task("My Task #2");
        errands.addTask(task2);

        ValidationResult res = new NodeTreeValidator().validate(errands);
        if (!res.isSuccessful()) {
            throw new IllegalStateException("The tree is invalid: " + res);
        }

        // Access the model
        List<Task> tasks = errands.getTasks();
        System.out.println("Tasks found: " + tasks.size());
        for (Task task : tasks) {
            System.out.println(" - " + task.getName());
        }
    }

    public static void main(String[] args) {
        new HeterogeneousAPIExample().useSpecificClasses();
    }
}
```

### Evaluation

- Full IDE support (auto-completion, navigation)
- Catch errors at compile time
- Clear API for collaborators
- Require extra work for defining the classes

## Suggested approach

- Use `DynamicNode` in **model editors**, **importers**, **migrators**
- Use custom classes (like `PersonNode`) in **interpreters**, **generators**, **type checkers**

## Interoperability

Both approaches can co-exist. For example, you might parse a file into `DynamicNode` objects and then convert them into typed classes using a factory or builder.
