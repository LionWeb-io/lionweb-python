---
sidebar_position: 43
---

# Serialization in LionWeb Java

The LionWeb Java library provides robust support for **serializing** and **deserializing** models composed of nodes. These nodes can represent instances of a language as well as the language definitions themselves.

Serialization is essential to:
- Communicate with a LionWeb-compliant repository.
- Store models on disk or transmit them over the network.
- Load them back into memory and process them.
- Maintain compatibility across clients and systems.

## Homogeneous Serialization

When working with the **homogeneous API**, such as `DynamicNode`, the LionWeb Java library provides default serialization mechanisms that can be used out of the box.

The following example demonstrates how to:
1. Define a small language consisting of `TaskList` and `Task` concepts.
2. Create model instances using `DynamicNode` subclasses.
3. Serialize the model using the standard JSON serializer.
4. Deserialize the JSON back into nodes.

```java
// After creating nodes (see below), serialize them:
JsonSerialization serialization = SerializationProvider.getStandardJsonSerialization();
String serialized = serialization.serializeTreesToJsonString(taskList);

// Deserialize with DynamicNode support:
serialization.enableDynamicNodes();
Node deserialized = serialization.deserializeToNodes(serialized).get(0);
```

If you do not enable dynamic nodes or register deserializers, the deserialization of unknown node types will throw an error.

## Custom Deserialization with Heterogeneous Nodes

When using custom node classes (i.e., heterogeneous nodes), you need to **register a custom deserializer** per concept to instantiate the correct subclass:

```java
serialization.getInstantiator().registerCustomDeserializer(taskConcept.getID(),
    (Instantiator.ClassifierSpecificInstantiator<Task>)
      (classifier, serializedInstance, deserializedNodesByID, propertiesValues) -> 
        new Task(serializedInstance.getID(), (String) propertiesValues.get(nameProperty)));
```

This allows you to benefit from type-safe APIs and static checking during development.

### Example

```java
// Create a task list and tasks
TaskList errands = new TaskList();
Task task1 = new Task("Buy milk");
Task task2 = new Task("Write report");
errands.addTask(task1);
errands.addTask(task2);

// Validate
ValidationResult res = new NodeTreeValidator().validate(errands);
if (!res.isSuccessful()) {
    throw new IllegalStateException("Invalid model");
}

// Serialize
JsonSerialization serialization = SerializationProvider.getStandardJsonSerialization();
String json = serialization.serializeTreesToJsonString(errands);
System.out.println(json);

// Deserialize
serialization.enableDynamicNodes(); // or register deserializers
Node restored = serialization.deserializeToNodes(json).get(0);
```

## Serializing Language Definitions

LionWeb Java treats languages as regular node trees:
- Concepts, Properties, Containments, and the Language itself are just nodes.
- The default serializer knows how to instantiate these standard types.

So, you can also do:

```java
String languageJson = serialization.serializeTreesToJsonString(myLanguage);
List<Node> deserializedLanguageElements = serialization.deserializeToNodes(languageJson);
```

No special registration is required for built-in language elements like `Language`, `Concept`, etc.—their deserializers are pre-registered in the standard serializer.

## A complete example

By combining dynamic and custom deserialization strategies, LionWeb Java offers both flexibility and strong typing for working with serialized models and metamodels.

```java
package com.example;

import io.lionweb.lioncore.java.language.*;
import io.lionweb.lioncore.java.model.ClassifierInstance;
import io.lionweb.lioncore.java.model.Node;
import io.lionweb.lioncore.java.model.impl.DynamicNode;
import io.lionweb.lioncore.java.serialization.Instantiator;
import io.lionweb.lioncore.java.serialization.JsonSerialization;
import io.lionweb.lioncore.java.serialization.SerializationProvider;
import io.lionweb.lioncore.java.serialization.data.SerializedClassifierInstance;
import io.lionweb.lioncore.java.utils.NodeTreeValidator;
import io.lionweb.lioncore.java.utils.ValidationResult;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

public class SerializationAPIExample {

  private static Concept taskListConcept;
  private static Concept taskConcept;
  private static Property nameProperty;
  private static Containment tasksContainment;
  private static Language taskLanguage;

  {
    defineLanguage();
  }

  private static class TaskList extends DynamicNode {
    TaskList(String id) {
      super(id, taskListConcept);
    }

    TaskList() {
      this(UUID.randomUUID().toString());
    }

    void addTask(Task task) {
      addChild(tasksContainment, task);
    }

    List<Task> getTasks() {
      return getChildren(tasksContainment).stream().map(n -> (Task) n).collect(Collectors.toList());
    }
  }

  private static class Task extends DynamicNode {
    Task(String name) {
      this(UUID.randomUUID().toString(), name);
    }

    Task(String id, String name) {
      super(id, taskConcept);
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
    tasksContainment =
        new Containment()
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

  public TaskList createTaskList() {
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

    return errands;
  }

  public static void main(String[] args) {
    SerializationAPIExample example = new SerializationAPIExample();
    TaskList taskList = example.createTaskList();
    JsonSerialization serialization = SerializationProvider.getStandardJsonSerialization();

    String serialized = serialization.serializeTreesToJsonString(taskList);
    System.out.println("== Tasks list ==");
    System.out.println(serialized);
    System.out.println();

    try {
      serialization.deserializeToNodes(serialized);
      throw new RuntimeException("We expect an exception");
    } catch (IllegalArgumentException e) {
      // We expect this
      System.out.println("Expected error: " + e.getMessage());
    }

    serialization.enableDynamicNodes();;
    Node deserialized1 = serialization.deserializeToNodes(serialized).get(0);
    System.out.println("First deserialization - Deserialized as " + deserialized1.getClass().getSimpleName());
    if (!taskList.equals(deserialized1)) {
      throw new IllegalStateException();
    }

    serialization.getInstantiator().registerCustomDeserializer(taskListConcept.getID(),
            (Instantiator.ClassifierSpecificInstantiator<TaskList>)
                    (classifier,
                     serializedClassifierInstance,
                     deserializedNodesByID,
                     propertiesValues) -> {
                      return new TaskList(serializedClassifierInstance.getID());
                    });
    serialization.getInstantiator().registerCustomDeserializer(taskConcept.getID(),
            (Instantiator.ClassifierSpecificInstantiator<Task>)
                    (classifier,
                     serializedClassifierInstance,
                     deserializedNodesByID,
                     propertiesValues) -> {
                      return new Task(serializedClassifierInstance.getID(), (String) propertiesValues.get(nameProperty));
                    });
    Node deserialized2 = serialization.deserializeToNodes(serialized).get(0);
    System.out.println("Second deserialization - Deserialized as " + deserialized2.getClass().getSimpleName());
    if (!taskList.equals(deserialized2)) {
      throw new IllegalStateException();
    }
  }
}
```