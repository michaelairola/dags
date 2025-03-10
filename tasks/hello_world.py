from airflow.models import Variable

test_variable = Variable.get("TEST")

print("test_variable:", test_variable)
