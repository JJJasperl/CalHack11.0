import pandas as pd
import openai
import os


def read_data(data_path, chunk_size):
    """
    Read all menu data, return string for prompting.
    :param data_path[string]
    :param chunk_size[int]
    :return: menu_data[string]
    """
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        return chunk.to_string()


def generatePrompting(customer_input):
    prompt = f"""
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
        selected_column.to_csv("./Assets/Data/selectedColumn.csv")


def testMatchMenuWithUserInput(prompt, user_input):
    """
    No Use, it is used for test
    :param prompt:
    :param user_input:
    :return:
    """
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


if __name__ == "__main__":
    # Config parameters
    raw_data_path = "../Assets/Data/menu.csv"
    chunk_size = 1000 # In case data size is too large.
    preProcessData(raw_data_path, chunk_size)

    # Read Data
    data_path = "../Assets/Data/selectedColumn.csv"
    menu_data = read_data(data_path=data_path, chunk_size=chunk_size)

    user_input = "Can I have a large double cheeseburger combo meal"
    # testMatchMenuWithUserInput(user_input)