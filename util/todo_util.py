import json
FILEPATH = "data/todos.json"


def todo_add(user, todo_text):
    with open(FILEPATH, "r+") as f:
        todo_dict = json.load(f)  # loads the todo's as a dict

        if user in todo_dict.keys():  # goes through each user
            # appends the new item into the dict
            todo_dict[user].append(todo_text)
        else:
            # if user has never been cached it creates a new user with a new todo list
            todo_dict[user] = [todo_text]

        f.seek(0)  # moves cursor to beginning of file
        f.truncate(0)  # deletes file contents
        json.dump(todo_dict, f, indent=6)  # loads the new dict into the file

        return f"Added **{todo_text}** to your todo list!"


def todo_view(user):
    with open(FILEPATH, "r") as f:
        todo_dict = json.load(f)  # loads the file into a dict

    # if user is in the keys and not empty []
    if user in todo_dict.keys() and todo_dict[user]:
        return todo_dict[user]  # returns the list

    return []  # returns empty list only if the user doesn't exist/doesn't have todo's


def todo_delete(user, index):
    with open(FILEPATH, "r+") as f:
        todo_dict = json.load(f)  # loads the file into a dict

        # catches type errors
        try:
            index = int(index)
        except:
            return "Index not in proper format. Make sure index is positive non-zero integer."

        # if user is in the keys and not empty []
        if user in todo_dict.keys() and todo_dict[user]:

            # if the index is outside the bounds
            if index > len(todo_dict[user]) or index <= 0:
                return f"Could not find item at position **{index}** in todo list"
            else:
                # stores the deleted item and removes it
                deleted_item = todo_dict[user].pop(index-1)
                f.seek(0)  # moves cursor to beginning of file
                f.truncate(0)  # deletes file contents
                # dumps the new dictionary without the deleted item
                json.dump(todo_dict, f, indent=6)
                return f"Deleted **{index}.) {deleted_item}** from your todo list!"

        else:  # if the user doesn't exist/has no todo's
            return "You have nothing in your todo list"
