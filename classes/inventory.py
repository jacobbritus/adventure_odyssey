# 1. player.inventory = Inventory()

# 2. player.inventory.add_item(item_name, quantity)

# 3. enemy.drop = Item(sword, None, 1)


class Item:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity


class Inventory:
    def __init__(self):
        self.items = {"potion": 10000}

    def add(self, item):
        if item.name in self.items.keys():
            self.items[item.name] += item.quantity
        else:
            self.items[item.name] = item.quantity