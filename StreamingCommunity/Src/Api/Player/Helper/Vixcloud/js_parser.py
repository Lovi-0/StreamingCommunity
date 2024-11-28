# 26.11.24
# !!! DIO CANErino

import re


class JavaScriptParser:
    @staticmethod
    def fix_string(ss):
        if ss is None:
            return None
        
        ss = str(ss)
        ss = ss.encode('utf-8').decode('unicode-escape')
        ss = ss.strip("\"'")
        ss = ss.strip()
        
        return ss
    
    @staticmethod
    def fix_url(url):
        if url is None:
            return None

        url = url.replace('\\/', '/')
        return url

    @staticmethod
    def parse_value(value):
        value = JavaScriptParser.fix_string(value)

        if 'http' in str(value) or 'https' in str(value):
            return JavaScriptParser.fix_url(value)
        
        if value is None or str(value).lower() == 'null':
            return None
        if str(value).lower() == 'true':
            return True
        if str(value).lower() == 'false':
            return False
        
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                pass
        
        return value

    @staticmethod
    def parse_object(obj_str):
        obj_str = obj_str.strip('{}').strip()
        
        result = {}
        key_value_pairs = re.findall(r'([\'"]?[\w]+[\'"]?)\s*:\s*([^,{}]+|{[^}]*}|\[[^\]]*\]|\'[^\']*\'|"[^"]*")', obj_str)
        
        for key, value in key_value_pairs:
            key = JavaScriptParser.fix_string(key)
            value = value.strip()

            if value.startswith('{'):
                result[key] = JavaScriptParser.parse_object(value)
            elif value.startswith('['):
                result[key] = JavaScriptParser.parse_array(value)
            else:
                result[key] = JavaScriptParser.parse_value(value)
        
        return result

    @staticmethod
    def parse_array(arr_str):
        arr_str = arr_str.strip('[]').strip()
        result = []
        
        elements = []
        current_elem = ""
        brace_count = 0
        in_string = False
        quote_type = None

        for char in arr_str:
            if char in ['"', "'"]:
                if not in_string:
                    in_string = True
                    quote_type = char
                elif quote_type == char:
                    in_string = False
                    quote_type = None
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == ',' and brace_count == 0:
                    elements.append(current_elem.strip())
                    current_elem = ""
                    continue
            
            current_elem += char
        
        if current_elem.strip():
            elements.append(current_elem.strip())
        
        for elem in elements:
            elem = elem.strip()
            
            if elem.startswith('{'):
                result.append(JavaScriptParser.parse_object(elem))
            elif 'active' in elem or 'url' in elem:
                key_value_match = re.search(r'([\w]+)\":([^,}]+)', elem)

                if key_value_match:
                    key = key_value_match.group(1)
                    value = key_value_match.group(2)
                    result[-1][key] = JavaScriptParser.parse_value(value.strip('"\\'))
            else:
                result.append(JavaScriptParser.parse_value(elem))
        
        return result

    @classmethod
    def parse(cls, js_string):
        assignments = re.findall(r'window\.(\w+)\s*=\s*([^;]+);?', js_string, re.DOTALL)
        result = {}
        
        for var_name, value in assignments:
            value = value.strip()
            
            if value.startswith('{'):
                result[var_name] = cls.parse_object(value)
            elif value.startswith('['):
                result[var_name] = cls.parse_array(value)
            else:
                result[var_name] = cls.parse_value(value)
        
        can_play_fhd_match = re.search(r'window\.canPlayFHD\s*=\s*(\w+);?', js_string)
        if can_play_fhd_match:
            result['canPlayFHD'] = cls.parse_value(can_play_fhd_match.group(1))
        
        return result
