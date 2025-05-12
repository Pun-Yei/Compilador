from nodos import *

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.funcion_actual = None  # Para rastrear la funcion actual
        self.tipo_retorno_actual = None  # Para validar returns
        
    def analizar(self, nodo):
        if isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
            return
            
        if isinstance(nodo, NodoFuncion):
            # Registrar la funcion en la tabla de simbolos
            self.funcion_actual = nodo.nombre
            self.tipo_retorno_actual = nodo.parametros[0].tipo if nodo.parametros else 'void'
            
            tipos_parametros = [p.tipo for p in nodo.parametros]
            self.tabla_simbolos.declarar_funcion(nodo.nombre, self.tipo_retorno_actual, tipos_parametros)
            
            # Registrar parametros como variables
            for param in nodo.parametros:
                self.tabla_simbolos.declarar_variable(param.nombre, param.tipo)
                
            # Analizar cuerpo de la funcion
            for instruccion in nodo.cuerpo:
                self.analizar(instruccion)
                
            # Resetear despues de analizar la funcion
            self.funcion_actual = None
            self.tipo_retorno_actual = None
            
        elif isinstance(nodo, NodoComparacion):
            # Analizar ambos lados de la comparacion
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            
            # Verificar que los tipos sean compatibles
            if tipo_izq != tipo_der:
                raise Exception(f"Error semantico: tipos incompatibles en comparacion {tipo_izq} {nodo.operador} {tipo_der}")
            
            # Las comparaciones siempre devuelven un entero (1 para verdadero, 0 para falso)
            return 'int'
                
        elif isinstance(nodo, NodoAsignacion):
            # Verificar si la variable esta declarada o declararla
            tipo_expr = self.analizar(nodo.expresion)
            if nodo.nombre[1] in self.tabla_simbolos.variables:
                # Verificar compatibilidad de tipos si la variable ya existe
                tipo_existente = self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1])
                if tipo_existente != tipo_expr:
                    raise Exception(f"Error semantico: tipo incompatible en asignacion. Variable '{nodo.nombre[1]}' es de tipo {tipo_existente} pero se le asigna {tipo_expr}")
            else:
                self.tabla_simbolos.declarar_variable(nodo.nombre[1], tipo_expr)
                
        elif isinstance(nodo, NodoIdentificador):
            # Verificar que la variable exista
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1])
            
        elif isinstance(nodo, NodoNumero):
            return 'int' if '.' not in nodo.valor[1] else 'float'
            
        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq != tipo_der:
                raise Exception(f"Error semantico: tipos incompatibles en operacion {tipo_izq} {nodo.operador} {tipo_der}")
            return tipo_izq
            
        elif isinstance(nodo, NodoLlamadaFuncion):
            # Verificar que la funcion exista
            tipo_retorno, tipos_parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre)
            
            # Verificar numero de argumentos
            if len(nodo.argumentos) != len(tipos_parametros):
                raise Exception(f"Error semantico: la funcion '{nodo.nombre}' espera {len(tipos_parametros)} argumentos pero se proporcionaron {len(nodo.argumentos)}")
            
            # Verificar tipos de argumentos
            for i, (arg, tipo_esperado) in enumerate(zip(nodo.argumentos, tipos_parametros)):
                tipo_arg = self.analizar(arg)
                if tipo_arg != tipo_esperado:
                    raise Exception(f"Error semantico: en argumento {i+1} de '{nodo.nombre}'. Se esperaba {tipo_esperado} pero se obtuvo {tipo_arg}")
            
            return tipo_retorno
            
        elif isinstance(nodo, NodoRetorno):
            tipo_retorno = self.analizar(nodo.expresion)
            if tipo_retorno != self.tipo_retorno_actual:
                raise Exception(f"Error semantico: la funcion '{self.funcion_actual}' debe retornar {self.tipo_retorno_actual} pero se encontro {tipo_retorno}")
            return tipo_retorno
            
        elif isinstance(nodo, NodoWhile):
            tipo_condicion = self.analizar(nodo.condicion)
            if tipo_condicion != 'int':  # Se asume que las condiciones son enteras (0 = false, !0 = true)
                raise Exception(f"Error semantico: la condicion del while debe ser de tipo 'int' pero es {tipo_condicion}")
            
            for instr in nodo.cuerpo:
                self.analizar(instr)
                
        elif isinstance(nodo, NodoFor):
            self.analizar(nodo.inicializacion)
            
            tipo_condicion = self.analizar(nodo.condicion)
            if tipo_condicion != 'int':
                raise Exception(f"Error semantico: la condicion del for debe ser de tipo 'int' pero es {tipo_condicion}")
            
            self.analizar(nodo.incremento)
            
            for instr in nodo.cuerpo:
                self.analizar(instr)
                
        elif isinstance(nodo, NodoIf):
            tipo_condicion = self.analizar(nodo.condicion)
            if tipo_condicion != 'int':
                raise Exception(f"Error semantico: la condicion del if debe ser de tipo 'int' pero es {tipo_condicion}")
            
            # Analizar el cuerpo del if
            for instruccion in nodo.cuerpo_if:
                self.analizar(instruccion)
            
            # Analizar los else if si existen
            for cond, cuerpo in nodo.else_ifs:
                tipo_cond = self.analizar(cond)
                if tipo_cond != 'int':
                    raise Exception(f"Error semantico: la condicion del else if debe ser de tipo 'int' pero es {tipo_cond}")
                for instr in cuerpo:
                    self.analizar(instr)
            
            # Analizar el else si existe
            if nodo.cuerpo_else:
                for instruccion in nodo.cuerpo_else:
                    self.analizar(instruccion)
        
        return None

class TablaSimbolos:
    def __init__(self):
        self.variables = {}  # {nombre: (tipo, es_constante)}
        self.funciones = {}  # {nombre: (tipo_retorno, [tipos_parametros])}
        
    def declarar_variable(self, nombre, tipo, es_constante=False):
        if nombre in self.variables:
            raise Exception(f'Error semantico: la variable {nombre} ya esta declarada')
        self.variables[nombre] = (tipo, es_constante)
        
    def obtener_tipo_variable(self, nombre):
        if nombre not in self.variables:
            raise Exception(f'Error semantico: la variable {nombre} no esta declarada')
        return self.variables[nombre][0]  # Devuelve solo el tipo
        
    def declarar_funcion(self, nombre, tipo_retorno, parametros):
        if nombre in self.funciones:
            raise Exception(f'Error semantico: la funcion {nombre} ya esta declarada')
        self.funciones[nombre] = (tipo_retorno, parametros)
        
    def obtener_info_funcion(self, nombre):
        if nombre not in self.funciones:
            raise Exception(f'Error semantico: la funcion {nombre} no esta declarada')
        return self.funciones[nombre]
    
    # Nuevo metodo para obtener todas las claves (variables + funciones)
    def keys(self):
        variables_keys = list(self.variables.keys())
        funciones_keys = list(self.funciones.keys())
        return variables_keys + funciones_keys
    
    # Nuevo metodo para obtener un valor por clave
    def get(self, key):
        if key in self.variables:
            return {'tipo': self.variables[key], 'tipo_entidad': 'variable'}
        elif key in self.funciones:
            tipo_retorno, parametros = self.funciones[key]
            return {'tipo': tipo_retorno, 'parametros': parametros, 'tipo_entidad': 'funcion'}
        return None
    
    # Metodo para imprimir la tabla de simbolos
    def __str__(self):
        result = "Variables:\n"
        for var, tipo in self.variables.items():
            result += f"  {var}: {tipo}\n"
        
        result += "\nFunciones:\n"
        for func, (tipo_ret, params) in self.funciones.items():
            result += f"  {func}: retorna {tipo_ret}, parametros {params}\n"
        
        return result