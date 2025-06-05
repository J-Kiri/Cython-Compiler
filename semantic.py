def semantic_error(current_token, message):
    (_, lexeme, lin, col) = current_token

    print(f'Error on line {lin}, column {col}: {message}')
    raise Exception


class Semantic:
    def __init__(self, target_name):
        self.global_table = {}
        self.current_scope = None
        self.target = open(target_name, "wt")

    def finish(self):
        self.target.close()

    def generate(self, level, code):
        indentation = ' ' * 4 * level
        self.target.write(indentation + code + "\n")

    def declare_var(self, token, def_type): # Variable Declare
        (_, name, _, _) = token
        if name in self.current_scope:
            semantic_error(token, f"Variable '{name}' already declared")
        else:
            self.current_scope[name] = def_type

    def declare_func(self, token, return_type, param_list): # Function Declare
        (_, name, _, _) = token
        if name in self.global_table:
            semantic_error(token, f"Function '{name}' already declared")
        else:
            self.global_table[name] = (return_type, param_list, {})

    def enter_function_scope(self, name):   # Enter the scope of the function??
        (_, param_list, scope) = self.global_table[name]

        self.current_scope = scope
        for (token_param, def_type) in param_list:
            if token_param[1] in self.current_scope:
                semantic_error(token_param, f"Variable '{token_param[1]}' already declared")
            self.declare_var(token_param, def_type)

    # Verify the type and existence of ident
    def is_var(self, name):
        return name in self.current_scope

    def is_func(self, name):
        return name in self.global_table

    def get_var_info(self, name, token):
        if name not in self.current_scope:
            semantic_error(token, f"Identifier '{name}' not declared")
        return self.current_scope[name]

    def get_func_info(self, name, token):
        if name not in self.global_table:
            semantic_error(token, f"Function '{name}' not declared")
        return self.global_table[name]
