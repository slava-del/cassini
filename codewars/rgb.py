def rgb(r, g, b):
    # Clamp function to keep values in the range 0–255
    def clamp(value):
        return max(0, min(255, value))
    
    # Convert to hexadecimal and ensure two digits with uppercase letters
    return f"{clamp(r):02X}{clamp(g):02X}{clamp(b):02X}"



def rgb(r, g, b):
    round = lambda x: min(255, max(x, 0))
    return ("{:02X}" * 3).format(round(r), round(g), round(b))