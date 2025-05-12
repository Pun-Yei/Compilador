class NodoAST:
    # Clase base para todos los nodos del AST
    pass

    def traducir(self):
        raise NotImplementedError("Metodo traducir () no implementado en este nodo")
    def generar_codigo(self):
        raise NotImplementedError("Metodo generar_codigo () no implementado en este nodo")

class NodoFuncion(NodoAST):
    def __init__(self, nombre, parametros, cuerpo):
        self.nombre = nombre
        self.parametros = parametros
        self.cuerpo = cuerpo
        
    def traducir(self):
        params = ",".join(p.traducir() for p in self.parametros)
        cuerpo = "\n    ".join(c.traducir() for c in self.cuerpo)
        return f"def {self.nombre}({params}):\n    {cuerpo}"
    
    def generar_codigo(self):
        codigo = f'{self.nombre}:\n'
        codigo += "    push ebp\n"
        codigo += "    mov ebp, esp\n"
        codigo += "\n".join(c.generar_codigo() for c in self.cuerpo)
        codigo += "\n    mov esp, ebp\n"
        codigo += "    pop ebp\n"
        codigo += "    ret\n"
        return codigo

class NodoParametro(NodoAST):
    # Nodo que representa un parametro de funcion
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        return self.nombre[1]
    
    def generar_codigo(self):
        codigo = f'{self.nombre[1]}:\n'
        codigo += "\n".join(c.generar_codigo() for c in self.cuerpo)
        return codigo

class NodoAsignacion(NodoAST):
    def __init__(self, nombre, expresion):
        self.nombre = nombre 
        self.expresion = expresion
        
    def traducir(self):
        return f"{self.nombre[1]} = {self.expresion.traducir()}"
    
    def generar_codigo(self):
        codigo = self.expresion.generar_codigo()
        codigo += f"\n    mov [{self.nombre[1]}], eax ; asignar a {self.nombre[1]}"
        return codigo
        
class NodoOperacion(NodoAST):
    # Nodo que representa una operacion aritmetica
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador[1]} {self.derecha.traducir()}"

    def generar_codigo(self):
        codigo = []
        codigo.append(self.izquierda.generar_codigo())#cargar el operando izquierdo
        codigo.append('    push eax; guardar en la pila')#guardar en la pila

        codigo.append(self.derecha.generar_codigo())#cargar el operando derecho
        codigo.append('    pop ebx; recuperar el primer operando')# ebx = opoerando 1 y eax= operando 2

        if self.operador == '+':
            codigo.append('    add eax, ebx ; eax = eax + ebx')

        elif self.operador == '-':
            codigo.append('    sub ebx, eax; ebx = ebx - eax')
            codigo.append('    mov eax, ebx; eax = ebx')

        elif self.operador == '*':
            pass
        
        elif self.operador == '/':
            pass 

        return '\n'.join(codigo)

    def optimizar(self):
        if isinstance(self.izquierda, NodoOperacion):
            izquierda = self.izquierda.optimizar()
        else:
            izquierda = self.izquierda
        if isinstance(self.derecha, NodoOperacion):
            derecha = self.derecha.optimizar()
        else:
            derecha = self.derecha
        
        # Si ambos operandos son numeros, evaluamos la operacion
        if isinstance(izquierda, NodoNumero) and isinstance(derecha, NodoNumero):
            if self.operador == '+':
                return NodoNumero(izquierda.valor + derecha.valor)
            elif self.operador == '-':
                return NodoNumero(izquierda.valor - derecha.valor)
            elif self.operador == '*':
                return NodoNumero(izquierda.valor * derecha.valor)
            elif self.operador == '/' and derecha.valor != 0:
                return NodoNumero(izquierda.valor / derecha.valor)
            
        # Simplificacion algebraica
        if self.operador in ['+', '*', '-', '/']:
            # Normalizar el orden de los operandos (numeros a la derecha)
            if isinstance(izquierda, NodoNumero) and not isinstance(derecha, NodoNumero):
                izquierda, derecha = derecha, izquierda

            # Multiplicacion por 1
            if self.operador == '*' and isinstance(derecha, NodoNumero) and derecha.valor == 1:
                return izquierda
            if self.operador == '*' and isinstance(izquierda, NodoNumero) and izquierda.valor == 1:
                return derecha

            # Suma con 0
            if self.operador == '+' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
                return izquierda
            if self.operador == '+' and isinstance(izquierda, NodoNumero) and izquierda.valor == 0:
                return derecha

            # Multiplicacion por 0
            if self.operador == '*' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
                return NodoNumero(0)
            if self.operador == '*' and isinstance(izquierda, NodoNumero) and izquierda.valor == 0:
                return NodoNumero(0)

            # Suma con negativo
            if self.operador == '+' and isinstance(derecha, NodoOperacion) and derecha.operador == '-' and isinstance(derecha.derecha, NodoNumero):
                return NodoOperacion(izquierda, '-', derecha.derecha)

            # Multiplicacion con negativo
            if self.operador == '*' and isinstance(derecha, NodoOperacion) and derecha.operador == '-' and isinstance(derecha.derecha, NodoNumero):
                return NodoOperacion(NodoOperacion(izquierda, '*', derecha.derecha), '-', NodoNumero(0))

            # Resta con 0
            if self.operador == '-' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
                return izquierda

            # Resta de un numero negativo
            if self.operador == '-' and isinstance(derecha, NodoOperacion) and derecha.operador == '-' and isinstance(derecha.derecha, NodoNumero):
                return NodoOperacion(izquierda, '+', derecha.derecha)

            # Resta de si mismo
            if self.operador == '-' and isinstance(izquierda, NodoIdentificador) and isinstance(derecha, NodoIdentificador):
                if izquierda.nombre == derecha.nombre:
                    return NodoNumero(0)

            # Division por 1
            if self.operador == '/' and isinstance(derecha, NodoNumero) and derecha.valor == 1:
                return izquierda

            # Division de si mismo
            if self.operador == '/' and isinstance(izquierda, NodoIdentificador) and isinstance(derecha, NodoIdentificador):
                if izquierda.nombre == derecha.nombre:
                    return NodoNumero(1)

            # Division de 0 por un numero
            if self.operador == '/' and isinstance(izquierda, NodoNumero) and izquierda.valor == 0:
                return NodoNumero(0)

            # Division por 0 (error)
            if self.operador == '/' and isinstance(derecha, NodoNumero) and derecha.valor == 0:
                raise ValueError("Error: División por cero.")
                
        # Si no se puede optimizar mas devolvemos la misma operacion
        return NodoOperacion(izquierda, self.operador, derecha)

class NodoRetorno(NodoAST):
    # Nodo que representa la sentencia return
    def __init__(self, expresion):
        self.expresion = expresion
        
    def traducir(self):
        return f"return {self.expresion.traducir()}"
    
    def generar_codigo(self):
        return self.expresion.generar_codigo() + '\n    ret ; retorno desde la subrutina'

class NodoIdentificador(NodoAST):
    def __init__(self, nombre):
        self.nombre = nombre
        
    def traducir(self):
        return self.nombre[1]

    def generar_codigo(self):
        return f"    mov eax, [{self.nombre[1]}] ; cargar variable {self.nombre[1]}"

class NodoNumero(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return str(self.valor[1])
        
    def generar_codigo(self):
        if '.' in self.valor[1] or 'f' in self.valor[1].lower():  # Es flotante
            return f"    movss xmm0, [{self.valor[1]}] ; cargar flotante {self.valor[1]}"
        else:  # Es entero
            return f"    mov eax, {self.valor[1]} ; cargar entero {self.valor[1]}"
      
class NodoLlamadaFuncion(NodoAST):
    # Nodo que representa una llamada a funcion
    def __init__(self, nombre, argumentos):
        self.nombre = nombre
        self.argumentos = argumentos
        
    def traducir(self):
        params = ",".join(p.traducir() for p in self.argumentos)
        return f"{self.nombre}({params})"
    
    def generar_codigo(self):
        codigo = []
        if self.nombre in ['printf', 'scanf']:
            # Argumentos en orden inverso (excepto el primero para printf)
            for arg in reversed(self.argumentos):
                codigo.append(arg.generar_codigo())
                codigo.append("    push eax")
            
            # Llamada a la función
            codigo.append(f"    call _{self.nombre}")
            
            # Limpiar la pila
            if self.argumentos:
                codigo.append(f"    add esp, {4 * len(self.argumentos)}")
        else:
            ...
        return "\n".join(codigo)
        
class NodoPrograma(NodoAST):
    """
    Nodo que representa un programa completo.
    Contiene una lista de funciones.
    """
    def __init__(self, funciones):
        self.funciones = funciones
        
    def traducir(self):
        return self.funciones
    
    def generar_codigo(self):
        codigo = ""
        for funcion in self.funciones:
            codigo += funcion.generar_codigo() + "\n\n"
        return codigo
    
class NodoString(NodoAST):
    def __init__(self, valor):
        self.valor = valor
        
    def traducir(self):
        return self.valor[1]
        
    def generar_codigo(self):
        return f'    mov eax, {self.valor[1]} ; cargar string'
    
class NodoDeclaracion(NodoAST):
    def __init__(self, tipo, nombre):
        self.tipo = tipo
        self.nombre = nombre
        
    def traducir(self):
        return f"{self.tipo} {self.nombre};"
        
    def generar_codigo(self):
        return f"; Declaracion de variable: {self.tipo} {self.nombre}"
class NodoWhile(NodoAST):
    def __init__(self, condicion, cuerpo):
        self.condicion = condicion
        self.cuerpo = cuerpo
        
    def traducir(self):
        codigo = f"while {self.condicion.traducir()}:\n    " + "\n    ".join(c.traducir() for c in self.cuerpo)
        return codigo
    
    def generar_codigo(self):
        label_start = f"L{id(self)}_start"
        label_end = f"L{id(self)}_end"
        
        codigo = []
        codigo.append(f"{label_start}: ; inicio de bucle while")
        codigo.append(self.condicion.generar_codigo())
        codigo.append("    cmp eax, 0 ; comparar la condicion de bucle while")
        codigo.append(f"    je {label_end} ; terninar el bucle si la condicion es falsa")
        
        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())
        codigo.append(f"    jmp {label_start} ; volvar al inicio del bucle while")
        
        codigo.append(f"{label_end}: ; fin de bucle while")
        return "\n".join(codigo)
    
class NodoFor(NodoAST):
    def __init__(self, inicializacion, condicion, incremento, cuerpo):
        self.inicializacion = inicializacion
        self.condicion = condicion
        self.incremento = incremento
        self.cuerpo = cuerpo
    
    def traducir(self):
        codigo = f"{self.inicializacion.traducir()}\nwhile {self.condicion.traducir()}:\n    " + \
                 "\n    ".join(c.traducir() for c in self.cuerpo) + \
                 f"\n    {self.incremento.traducir()}"
        return codigo

    def generar_codigo(self):
        label_start = f"L{id(self)}_start"
        label_end = f"L{id(self)}_end"

        codigo = []
        codigo.append(self.inicializacion.generar_codigo())  # codigo de inicialización

        codigo.append(f"{label_start}: ; inicio del bucle for")
        codigo.append(self.condicion.generar_codigo())
        codigo.append("    cmp eax, 0 ; comparar la condicion del for")
        codigo.append(f"    je {label_end} ; salir del bucle si la condicion es falsa")

        for instruccion in self.cuerpo:
            codigo.append(instruccion.generar_codigo())

        codigo.append(self.incremento.generar_codigo())  # codigo del incremento
        codigo.append(f"    jmp {label_start} ; volver al inicio del bucle for")

        codigo.append(f"{label_end}: ; fin del bucle for")
        return "\n".join(codigo)


           
class NodoIf(NodoAST):
    def __init__(self, condicion, cuerpo_if, cuerpo_else=None, else_ifs=None):
        self.condicion = condicion
        self.cuerpo_if = cuerpo_if
        self.cuerpo_else = cuerpo_else
        self.else_ifs = else_ifs if else_ifs is not None else []
        
    def traducir(self):
        codigo = f"if {self.condicion.traducir()}:\n    " + "\n    ".join(c.traducir() for c in self.cuerpo_if)
        
        for cond, cuerpo in self.else_ifs:
            codigo += f"\nelif {cond.traducir()}:\n    " + "\n    ".join(c.traducir() for c in cuerpo)
            
        if self.cuerpo_else:
            codigo += "\nelse:\n    " + "\n    ".join(c.traducir() for c in self.cuerpo_else)
            
        return codigo
    
    def generar_codigo(self):
        codigo = []
        # Generar codigo para la condicion principal
        codigo.append(self.condicion.generar_codigo())
        
        label_end = f"L{id(self)}_end"
        label_next = f"L{id(self)}_next"
        
        codigo.append(f"    cmp eax, 0")
        codigo.append(f"    je {label_next}")
        
        # Codigo para el cuerpo if
        for instruccion in self.cuerpo_if:
            codigo.append(instruccion.generar_codigo())
        codigo.append(f"    jmp {label_end}")
        
        # Codigo para los else if
        for i, (cond, cuerpo) in enumerate(self.else_ifs):
            codigo.append(f"{label_next}:")
            label_next = f"L{id(self)}_next_{i}"
            
            codigo.append(cond.generar_codigo())
            codigo.append(f"    cmp eax, 0")
            codigo.append(f"    je {label_next}")
            
            for instruccion in cuerpo:
                codigo.append(instruccion.generar_codigo())
            codigo.append(f"    jmp {label_end}")
        
        # Codigo para el else (si existe)
        if self.cuerpo_else:
            codigo.append(f"{label_next}:")
            for instruccion in self.cuerpo_else:
                codigo.append(instruccion.generar_codigo())
        
        codigo.append(f"{label_end}:")
        return "\n".join(codigo)
class NodoIncremento(NodoAST):
    def __init__(self, variable, valor=None, tipo="++"):
        self.variable = variable
        self.valor = valor
        self.tipo = tipo

    def traducir(self):
        if self.tipo == "++":
            return f"{self.variable} += 1"
        elif self.tipo == "--":
            return f"{self.variable} -= 1"
        else:
            return f"{self.variable} = {self.valor.traducir()}"

    def generar_codigo(self):
        if self.tipo == "++":
            return f"    mov eax, [{self.variable}]\n    add eax, 1\n    mov [{self.variable}], eax  ; {self.variable}++"
        elif self.tipo == "--":
            return f"    mov eax, [{self.variable}]\n    sub eax, 1\n    mov [{self.variable}], eax  ; {self.variable}--"
        else:  # Asignacion normal
            return f"    mov eax, {self.valor.generar_codigo()}  ; Cargar el valor en eax\n    mov [{self.variable}], eax  ; Asignar el valor a {self.variable}"


class NodoComparacion(NodoAST):
    def __init__(self, izquierda, operador, derecha):
        self.izquierda = izquierda
        self.operador = operador
        self.derecha = derecha
        
    def traducir(self):
        return f"{self.izquierda.traducir()} {self.operador} {self.derecha.traducir()}"
    
    def generar_codigo(self):
        codigo = []
        # Cargar operando izquierdo
        codigo.append(self.izquierda.generar_codigo())
        codigo.append("    push eax")
        
        # Cargar operando derecho
        codigo.append(self.derecha.generar_codigo())
        codigo.append("    pop ebx")
        
        # Comparacion
        codigo.append("    cmp ebx, eax")
        
        # Configurar eax segun la comparacion
        if self.operador == '>':
            codigo.append("    setg al")
        elif self.operador == '<':
            codigo.append("    setl al")
        elif self.operador == '>=':
            codigo.append("    setge al")
        elif self.operador == '<=':
            codigo.append("    setle al")
        elif self.operador == '==':
            codigo.append("    sete al")
        elif self.operador == '!=':
            codigo.append("    setne al")
            
        codigo.append("    movzx eax, al")
        return "\n".join(codigo)
    
class NodoConstante(NodoAST):
    def __init__(self, tipo, nombre, valor):
        self.tipo = tipo
        self.nombre = nombre
        self.valor = valor
        
    def traducir(self):
        return f"const {self.tipo} {self.nombre} = {self.valor[1]};"
        
    def generar_codigo(self):
        return f"    {self.nombre} dd {self.valor[1]} ; constante {self.tipo}"
    