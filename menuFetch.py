import pandas as pd
import openai
import os


def preProcessData(data_path, chunk_size):
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        # Pick desired column names.
        selected_column = chunk.loc[:, ["Item", "Stock"]]

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
        selected_column.insert(2, "Size", new_column)
        prices = [10]*260
        selected_column.insert(3, "Price", prices)


        # print(selected_column)
        selected_column.to_csv("./Assets/Data/selectedColumn.csv")


def read_data(data_path, chunk_size):
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
    
    If user specifies the size of a meal, assign this size for all items in the combo.
    1. Compare the menu data with the user input, make sure the SIZE is correct.
    2. Generate a table of the order, with 4 column: Item, Quantity, Unit Price, Custom Message
    3. If you find confused description and can't fetch from the menu data, feel free to ask after the table.
    
    The return message should only be:
    * A table of the order with correct size input by the user
    * Follow-up Questions if needed
    
    In the table, item name must be aligned with names in the menu data. 
    """
    return prompt


def matchMenuWithUserInput(user_input):
    prompt = generatePrompting(menu_data, user_input)
    # Set your API key
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Create a chat completion
    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
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
menu_data = read_data(data_path=data_path, chunk_size=chunk_size)

# Show return data
pd.set_option('display.max_columns', None)


# user_input = "我可以要一个吉士汉堡吗和一个大可乐？"
user_input = "Can I have a large double cheeseburger meal"
# user_input = "Can I have two large double cheese burger meals, one with diet cola and french fries, another with sprite"
# user_input = "我可以要一个双层吉士汉堡大套餐吗？"
# user_input = "1 + 1 = ？"
# user_input = "May I have a sweet potato fries"
# user_input = "Can I get a Chicken Nuggets Combo with medium fries."
matchMenuWithUserInput(user_input)
