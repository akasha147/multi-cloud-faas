

def giveFunctionData(filename, function):
    function_content = ''
    data = open(filename)
    # Tells us whether to append lines to the `function_content` string
    record_content = False
    for line in data:
        if not record_content:
            # Once we find a match, we start recording lines
            if function in line and line.startswith('def'):
                function_content+=line
                record_content = True
        else:
            # We keep recording until we encounter another function
            if line.startswith('def'):
                break
            function_content+=line

    return function_content