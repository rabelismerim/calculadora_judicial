from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from security.formula.models import CalcFormula, Formula
from security.views import Security


class FormulaAdmin(admin.ModelAdmin):
    change_form_template = 'extend_admin_formula.html'
    readonly_fields = ['method', 'show_code', 'attr']
    exclude = ['code']

    def get_object(self, request, object_id, from_field=None):
        change_obj = super(FormulaAdmin, self).get_object(request, object_id, from_field=None)
        if request.method == 'GET' and request.GET.get('view_code') and request.user.has_permission('view_formula'):
            obj = Formula.objects.get(id=object_id)
            change_obj.code = Security().decrypt(obj.code)
        return change_obj

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_perm_view_formula'] = request.user.has_permission('view_formula')

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

    @admin.display(description='Code')
    def show_code(self, obj):
        code = obj.code
        if str(code).startswith('gAAAAAB'):
            return code
        return format_html('<div><pre>{0}</pre></div>', code)


admin.site.register(Formula, FormulaAdmin)


class CalcFormulaAdmin(admin.ModelAdmin):
    model = CalcFormula
    readonly_fields = ['show_formulas', 'object_id', 'content_type', 'calculation']
    exclude = ['formulas']

    @admin.display(description='Formulas')
    def show_formulas(self, obj):
        formulas = obj.formulas.all()
        list_href = []
        for formula in formulas:
            detail_view_url = reverse('admin:formula_formula_change', args=[formula.id])
            href_certificate = format_html('<a href="{0}" target="_blank">{1}</a>', detail_view_url, formula.method)
            list_href.append(href_certificate)
        return format_html("<br>".join(list_href))


admin.site.register(CalcFormula, CalcFormulaAdmin)
