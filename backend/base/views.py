import inspect

from security.formula.models import CalcFormula, Formula
from calculation.models import Calculation


class ExtractFormula:
    """A utility class for extracting formulas used in a calculation

    **Usage**

        The `ExtractFormula` class is a utility class that extracts formulas used in a calculation. To use this class,
        simply create an instance of it and call the `get_methods` method, passing in a list of the classes from which
        you want to extract the formulas.

    **Example**
        class A:
            def method_1(self):
                x = 1
                y = 2
                return x + y

            def method_2(self):
                z = 3
                return self.method_1() + z

        class B(A):
            def method_3(self):
                return self.method_1() * self.method_2()

        To extract the formulas used in the `B` class, you could do the following:
            from myapp.models import Calculation
            from myapp.utils import ExtractFormula

            instance = Fund() The related calculation object
            calculation = instance.calculation

            extractor = ExtractFormula(instance, calculation, ['method_3'])

            formulas = extractor.get_methods([B])
    """

    @staticmethod
    def __get_attributes(cls) -> list:
        """Get a list of attributes for the given class"""
        attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        attributes = [a for a in attributes if not (a[0].startswith('__') and a[0].endswith('__'))]
        return attributes

    def __init__(self, instance, calculation: Calculation, included_method_names):
        """Instantiate an ExtractFormula object"""
        self.__instance = instance
        self.__calculation = calculation
        self.__included_method_names = included_method_names

    def __get_methods(self, cls) -> list:
        """Recursively get a list of methods for a class and its base classes"""
        if inspect.isclass(cls):
            methods = inspect.getmembers(cls, predicate=inspect.isfunction)
        elif inspect.isfunction(cls):
            methods = [(cls.__name__, cls)]
        else:
            raise ValueError("Invalid object type. Expected class or function.")

        list_methods = []
        for name, method in methods:

            has_method = method.__name__ in self.__included_method_names or name in self.__included_method_names
            if not has_method:
                continue
            source_code = inspect.getsource(method)
            total_lines = source_code.count('\n')
            list_methods.append(
                {'method': f"{cls.__name__}.{name}_{total_lines}_{len(source_code)}", 'code': source_code})

        if hasattr(cls, '__bases__'):
            for base_cls in cls.__bases__:
                self.__get_methods(base_cls)
        return list_methods

    def get_methods(self, cls: list) -> list:
        """Extract the methods and their source code from a list of classes"""
        methods = []
        for cl in cls:
            methods.extend(self.__get_methods(cl))

        calc_formula = CalcFormula.objects.filter(object_id=self.__instance.id, calculation=self.__calculation).first()

        if not calc_formula:
            calc_formula = CalcFormula.objects.create(object_id=self.__instance.id, content_object=self.__instance,
                                                      calculation=self.__calculation)
        for method in methods:
            formula, created = Formula.objects.get_or_create(defaults=method, **{'method': method['method']})
            calc_formula.formulas.add(formula.id)
        calc_formula.save()
        return methods
