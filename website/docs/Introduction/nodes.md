---
title: LionWeb Nodes
sidebar_position: 30
---

# Overview of the LionWeb Model

At the core of the LionWeb systems are **nodes**, which are organized into **trees**, and grouped into **partitions**.

Collections of _partitions_ can be informally referred to as _models_.

## Trees and Partitions

In LionWeb, data is organized into **trees of nodes**. Each individual tree is called a **partition**, which:

- Has exactly **one root node**
- Each node can contain **zero or more children**, organized through named **containments**
- The tree can grow arbitrarily deep, with no limit on the number of children or levels of nesting

Each containment defines a specific slot under which children may appear.

## Nodes

Each **node** in LionWeb has several important characteristics:

- It has a globally unique **ID**, allowing it to be referenced uniquely.
- It may contain a set of **properties**, which are named primitive values (e.g., strings, integers, booleans).
- It may contain children, under several **containments**
- It can hold **references** to other nodes, allowing for graph-like interconnections across trees.
- It is an **instance of a Concept**, which defines its structure. This means that all nodes 
  which are instances of the same *Concept** will have the same *properties*, *containments*, and *references*, even if
  they could be empty for some instances.

## Properties

**Properties** represent the primitive values associated with a node. These are defined by the Concept and can include values such as:

- `name: "MyClass"`
- `visibility: public`
- `isAbstract: false`

The Concept determines:

- Which properties are available
- The type of each property
- Whether a property is **required** or **optional&&

## References

Nodes may contain **references** to other nodes, forming non-tree links between elements. Each reference can hold zero, one, or more reference values.
Each reference value has:

- A **`resolveInfo`** field: a string representing the logical name or identifier to be used during resolution (e.g., `"B"` in `class A extends B`)
- An optional **`referenced`** field: this contains the **ID** of the node that the reference actually points to, once resolved

This dual mechanism allows references to exist before they are resolved, supporting workflows like parsing incomplete models or deferring resolution to later phases.

For example:

```java
class A extends B { }
```

In this case:
* The reference to B would have resolveInfo = "B"
* If the class B is defined elsewhere and known, then referenced will point to the node ID for B

## Concepts and Structure

Each node is an instance of a Concept, and the Concept defines the nodess shape:
* Properties: what primitive values the node can or must carry
* Containments: what children it can have and in which slots
* References: what links it can maintain to other nodes

Properties, containments, and references are all **features**.

Concepts enforce both the structure and constraints of the model, much like classes do in object-oriented programming.

To learn more about how languages define Concepts and other elements, see [Introduction to Languages](introduction-to-languages.md).