#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ScriptException(Exception):
    def __init__(self, str):
        self.str = str

    def _str_(self):
        return self.str
