---
title: Working with the LionWeb Repository
sidebar_position: 44
---

# Working with the LionWeb Repository

Working with the [LionWeb Repository](https://github.com/LionWeb-io/lionweb-repository) we can store and retrieve nodes. It is also a mean to exchange models with other LionWeb-compliant components. You can refer to the website of the LionWeb Repository to learn how to start it. 

This page provides an overview of how to interact with the repository using the provided Java client and outlines the basic concepts involved.

## Using Gradle

Add the following to your `build.gradle` or `build.gradle.kts`:

```kotlin
dependencies {
    // Previously added
    implementation("io.lionweb.lionweb-java:lionweb-java-2024.1-core:$lionwebVersion")
    // Specific for working with the LionWeb Repository
    implementation("io.lionweb.lionweb-java:lionweb-java-2024.1-repo-client:$lionwebVersion")
}
```

## Overview

The LionWeb Repository is a generic storage system designed to hold nodes conforming to the LionWeb metamodel.

It provides two sets of APIs:

* The Bulk APIs: intended to store and retrieve entire partitions or large sub-trees
* The Delta APIs: currently under development, it will support real-time collaboration

The LionWeb Repository can also optionally support versioning.

In this guide we will only focus on the Bulk APIs.

## Working with the Bulk APIs

It offers REST APIs for communication, which are wrapped in a convenient Java client: `LionWebRepoClient`. This client supports features like:

- Creating and managing **partitions** (top-level model containers)
- Storing and retrieving **nodes**
- Supporting multiple **LionWeb versions**
- Providing hooks for **functional testing**

## Example Usage

The following example demonstrates how to use the LionWeb Java client to:

1. Connect to a running LionWeb Repository
2. Define a language and register it
3. Create a partition node
4. Add children to that partition
5. Store and retrieve nodes

```java
LionWebRepoClient client =
        new LionWebRepoClient(LionWebVersion.v2023_1, "localhost", 3005, "myRepo");
client.getJsonSerialization().registerLanguage(PropertiesLanguage.propertiesLanguage);

DynamicNode p1 = new DynamicNode("p1", PropertiesLanguage.propertiesPartition);
client.createPartitions(client.getJsonSerialization().serializeNodesToJsonString(p1));

DynamicNode f1 = new DynamicNode("f1", PropertiesLanguage.propertiesFile);
ClassifierInstanceUtils.setPropertyValueByName(f1, "path", "my-path-1.txt");
DynamicNode f2 = new DynamicNode("f2", PropertiesLanguage.propertiesFile);
ClassifierInstanceUtils.setPropertyValueByName(f2, "path", "my-path-2.txt");
ClassifierInstanceUtils.addChild(p1, "files", f1);
ClassifierInstanceUtils.addChild(p1, "files", f2);

client.store(Collections.singletonList(p1));

List<Node> retrievedNodes1 = client.retrieve(Collections.singletonList("p1"), 10);
assertEquals(1, retrievedNodes1.size());
assertEquals(p1, retrievedNodes1.get(0));
```

### Creating partitions

Something to keep in mind is that the LionWeb Repository will only let us create partitions without children. So, we may need to create a partition and only then add children to it by invoking **store**.
