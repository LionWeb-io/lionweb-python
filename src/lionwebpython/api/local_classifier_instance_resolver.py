class LocalClassifierInstanceResolver:
    def __init__(self, *instances):
        self.instances = {instance.get_id(): instance for instance in instances}

    def add(self, instance):
        self.instances[instance.get_id()] = instance

    def resolve(self, instance_id):
        return self.instances.get(instance_id)

    def add_all(self, instances):
        for instance in instances:
            self.add(instance)

    def add_tree(self, root):
        self.add(root)
        for child in root.get_children():
            self.add_tree(child)

    def __str__(self):
        return f"LocalClassifierInstanceResolver({list(self.instances.keys())})"
