
from jinja2 import Template





table = '''
<table>
  <tr>
    {% for cell in header %}
      <td><b>{{ cell }}</b></td>
    {% endfor %}
  </tr>
  {% for row in fillups %}
    <tr>
      {% for cell in row %}
        <td>{{ cell }}</td>
      {% endfor %}
    </tr>
  {% endfor %} 
</table>
'''

table = '''
<table>
  <tr>
    {% for key,value in dict[0].items() %}
      <td><b>{{ key }}</b></td>
    {% endfor %}
  </tr>
  {% for dict_item in dict %}
    <tr>
      {% for key, value in dict_item.items() %}
        <td>{{ value }}</td>
      {% endfor %}
    </tr>
  {% endfor %} 
</table>
'''

dict = [{'name': 'A', 'title': 'AT'}, {'name': 'B', 'title': 'BT'}]

template = Template(table)
t = template.render(dict=dict)
print(t)
