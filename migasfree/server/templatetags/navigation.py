# -*- coding: utf-8 *-*
# from http://blog.scur.pl/2012/09/highlighting-current-active-page-django/

from django import template
from django.core import urlresolvers
from django.utils.encoding import smart_str

register = template.Library()

# Code to django 1.3

# http://djangosnippets.org/snippets/1113/


def parse_args_kwargs_and_as_var(parser, bits):
    args = []
    kwargs = {}
    as_var = None

    bits = iter(bits)
    for bit in bits:
        if bit == 'as':
            as_var = bits.next()
            break
        else:
            for arg in bit.split(","):
                if '=' in arg:
                    k, v = arg.split('=', 1)
                    k = k.strip()
                    kwargs[k] = parser.compile_filter(v)
                elif arg:
                    args.append(parser.compile_filter(arg))
    return args, kwargs, as_var


def get_args_and_kwargs(args, kwargs, context):
    out_args = [arg.resolve(context) for arg in args]
    out_kwargs = dict([(smart_str(k,'ascii'), v.resolve(context)) for k, v in kwargs.items()])
    return out_args, out_kwargs


@register.tag
def current_option(parser, token):
    bits = token.contents.split(' ')
    if len(bits) < 1:
        raise template.TemplateSyntaxError("'%s' takes at least one argument" % bits[0])

    if len(bits) > 1:
        args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, bits[1:])

    return CurrentOption(args, kwargs, as_var)


class CurrentOption(template.Node):
    def __init__(self, args, kwargs, as_var):
        self.args = args
        self.kwargs = kwargs
        self.as_var = as_var

    def current_url_equals(self, context, url_name, **kwargs):
        resolved = False
        try:
            resolved = urlresolvers.resolve(context.get('request').path)
        except:
            pass
        matches = resolved and resolved.url_name == url_name
        if matches and kwargs:
            for key in kwargs:
                kwarg = kwargs.get(key)
                resolved_kwarg = resolved.kwargs.get(key)
                if not resolved_kwarg or str(kwarg) != resolved_kwarg:
                    return False
        return matches

    def render(self, context):
        args, kwargs = get_args_and_kwargs(self.args, self.kwargs, context)
        ret = ' current'
        matches = self.current_url_equals(context, args[0], **kwargs)

        return ret if matches else ''


"""
Code to django 1.4

@register.simple_tag(takes_context=True)
def current_option(context, url_name, return_value=' current', **kwargs):
    matches = current_url_equals(context, url_name, **kwargs)
    return return_value if matches else ''


def current_url_equals(context, url_name, **kwargs):
    resolved = False
    try:
        resolved = urlresolvers.resolve(context.get('request').path)
    except:
        pass
    matches = resolved and resolved.url_name == url_name
    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False
    return matches
"""
