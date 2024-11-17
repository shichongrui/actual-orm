def int2():
    return {"data_type": "int2"}  # Small integer

def int4():
    return {"data_type": "int4"}  # Integer

def int8():
    return {"data_type": "int8"}  # Big integer

def float4():
    return {"data_type": "float4"}  # Single precision floating-point

def float8():
    return {"data_type": "float8"}  # Double precision floating-point

def numeric(precision: int | None = None, scale: int | None =None):
    # Numeric with optional precision and scale
    data_type = "numeric"
    if precision is not None and scale is not None:
        data_type += f"({precision}, {scale})"
    return {"data_type": data_type}

def serial():
    return {"data_type": "serial"}  # Auto-incrementing integer

def bigserial():
    return {"data_type": "bigserial"}  # Auto-incrementing big integer

def varchar(length:int):
    return {"data_type": f"varchar({length})"}  # Variable-length with limit

def char(length:int):
    return {"data_type": f"char({length})"}  # Fixed-length

def text():
    return {"data_type": "text"}  # Variable-length, unlimited size

def uuid():
    return {"data_type": "uuid"}

def date():
    return {"data_type": "date"}  # Date only

def timestamp(with_timezone=False, precision:int=3):
    # Timestamp with optional timezone
    return {"data_type": f"timestamptz({precision})" if with_timezone else "timestamp"}

def time(with_timezone=False):
    # Time with optional timezone
    return {"data_type": "timetz" if with_timezone else "time"}

def interval():
    return {"data_type": "interval"}  # Time interval

def data_type(data_type: str):
    return {"data_type": data_type}