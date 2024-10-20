import pandas as pd
import openai
import os


def preProcessData(data_path, chunk_size):
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        # Pick desired column names.
        selected_column = chunk.loc[:, ["Category", "Item", "Stock"]]

        # Get size info
        size_list = ["Regular", "Small", "Medium", "Large", "Child"]
        new_column = []
        for index, row in selected_column.iterrows():
            item = row["Item"]
            for size in size_list:
                if size in item:
                    new_column.append(size)
                    break

            if len(new_column) != index+1:
                new_column.append("NA")

        # Add one column
        selected_column.insert(3, "Size", new_column)

        print(selected_column)
        selected_column.to_csv("./Assets/Data/selectedColumn.csv")


def read_data(data_path):
    """
    Read all menu data, return string for prompting.
    :param data_path[string]
    :param chunk_size[int]
    :return: menu_data[string]
    """
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        return chunk.to_string()


def generatePrompting(menu_data, customer_input):
    prompt = f"""
    Given the following menu data:
    {menu_data}

    Here is the customer input:
    {customer_input}
    Please compare the menu data and the customer input, generate an applicable list of the order with the format 
    and the description below. Break down to multiple items if needed. If you find confused description and can't
    fetch from the menu data, feel free to ask.
    
    Item, Size, Quantity, Custom Message
    
    For item, if there's size description like small, medium, and large, remove it and show in Size column.
    For size, you should only include small, medium, and large, or xx piece;
    For quantity, it should be an integer;
    """
    return prompt


def matchMenuWithUserInput(user_input):
    prompt = generatePrompting(menu_data, user_input)
    # Set your API key
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Create a chat completion
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}])

    # Print the response
    print(completion.choices[0].message.content)

# Config parameters
raw_data_path = "./Assets/Data/menu.csv"
chunk_size = 1000 # In case data size is too large.
preProcessData(raw_data_path, chunk_size)



# Read Data
data_path = "./Assets/Data/selectedColumn.csv"
menu_data = read_data(data_path=data_path)

# Show return data
pd.set_option('display.max_columns', None)


# user_input = "May I have a double cheese burger without sauce, a medium french fries, and a large coke."
user_input = "Can I get a Chicken Nuggets Combo with medium fries."
matchMenuWithUserInput(user_input)




