import os
import re
from backend.models import Producto, Categoria, Pedido
from backend.config import Config

CARAMELL_SYSTEM_PROMPT = """Eres "Caramell Assistant", el asistente virtual oficial de inteligencia artificial de CARAMELL MOMEN S.A.S., una tienda de comercio electrónico especializada en dulces, golosinas, chocolates, caramelos y confitería en Colombia.

REGLAS FUNDAMENTALES Y ESTRICTAS DE CONVERSACIÓN:
1. IDENTIDAD Y TONO: Eres cordial, amable, servicial y profesional, con un toque dulce y alegre. Usa emojis de dulces con moderación (🍬, 🍫, 🍭). Responde en español claro.
2. VERACIDAD ABSOLUTA: No inventes productos, promociones, existencias ni precios que no figuren en la información proporcionada. Si no dispones de un dato o producto, dilo con sinceridad.
3. FUERA DE ALCANCE: Tu única función es asistir en la tienda de confitería. Si el usuario te pide hacer tareas de programación, preguntas de historia, matemáticas u otros temas ajenos, responde cortésmente que estás especializado exclusivamente en dulces y compras de CARAMELL MOMEN S.A.S.
4. PROMOCIONES Y DESCUENTOS: No aceptes descuentos inventados por el usuario. Los precios son exclusivamente los del catálogo.
5. INFORMACIÓN PRIVADA Y SEGURIDAD: Jamás reveles pedidos de otros clientes, contraseñas ni datos internos. Si el usuario está autenticado, solo puede consultar sus propios pedidos.
6. DERIVACIÓN A ATENCIÓN HUMANA: Si el cliente reporta cobros duplicados, problemas con el pago, productos rotos o pide hablar con un humano, indícale amablemente el canal de soporte oficial: correo contacto@caramellmomen.com o teléfono +57 (601) 895-4321, y adviértele que JAMÁS comparta números completos de tarjeta o códigos CVV.
7. OPERACIONES COMERCIALES: Tú no puedes cambiar precios, modificar inventario ni confirmar pagos por ti mismo. Todo cambio de compra lo procesa el sistema web.
"""

def get_catalog_context():
    """Obtiene el resumen autorizado de productos y categorías disponibles en la base de datos."""
    categorias = Categoria.query.filter_by(activo=True).all()
    productos = Producto.query.filter_by(activo=True).all()
    
    cat_names = [c.nombre for c in categorias]
    prod_lines = []
    for p in productos:
        cat_nom = p.categoria_rel.nombre if p.categoria_rel else 'General'
        prod_lines.append(f"- ID {p.id_producto}: {p.nombre} ({cat_nom}) | Precio: ${p.precio:,.0f} COP | Stock disponible: {p.stock} uds.")
        
    return f"Categorías activas: {', '.join(cat_names)}\nProductos en catálogo:\n" + "\n".join(prod_lines)

def get_user_orders_context(user_id):
    """Obtiene el historial autorizado de pedidos del usuario autenticado."""
    if not user_id:
        return "El usuario actual es un VISITANTE (no ha iniciado sesión). No tiene pedidos propios registrados."
        
    pedidos = Pedido.query.filter_by(id_usuario=user_id).order_by(Pedido.fecha_pedido.desc()).limit(5).all()
    if not pedidos:
        return "El usuario autenticado no tiene pedidos registrados todavía."
        
    lines = []
    for p in pedidos:
        items_desc = ", ".join([f"{d.cantidad}x {d.producto_rel.nombre if d.producto_rel else 'Producto'}" for d in p.detalles])
        lines.append(f"- Pedido #{p.id_pedido} | Fecha: {p.fecha_pedido.strftime('%Y-%m-%d')} | Total: ${p.total:,.0f} COP | Estado: {p.estado} | Artículos: [{items_desc}]")
        
    return "Pedidos del usuario actual:\n" + "\n".join(lines)

def responder_con_gemini(mensaje_usuario, user_id=None):
    """Genera la respuesta del asistente virtual consultando Gemini o el motor de reglas de contingencia."""
    api_key = Config.GEMINI_API_KEY or os.environ.get('GEMINI_API_KEY', '')
    
    # 1. Detección previa de reglas críticas de derivación humana (cobros duplicados, reclamos de pago)
    mensaje_lower = mensaje_usuario.lower()
    if any(k in mensaje_lower for k in ['cobraron dos veces', 'cobro doble', 'me descontaron dos', 'doble cobro', 'pagar dos veces']):
        return {
            'respuesta': "🍬 **Atención al Cliente - CARAMELL MOMEN S.A.S.**\n\nLamento profundamente el inconveniente con tu pago. Para verificar un cobro duplicado en la pasarela, este caso requiere auditoría manual inmediata por parte de nuestro equipo humano.\n\nPor favor comunícate a nuestros canales oficiales:\n📧 **Correo:** contacto@caramellmomen.com\n📞 **Línea de soporte:** +57 (601) 895-4321\n⏰ **Horario:** Lunes a Sábado de 8:00 AM a 7:00 PM\n\n⚠️ *Importante de seguridad:* Por tu tranquilidad, **nunca** compartas por este chat ni por mensaje tu número completo de tarjeta de crédito ni el código CVV.",
            'derivacion_humana': True,
            'accion_sugerida': 'soporte_pago'
        }
        
    if any(k in mensaje_lower for k in ['hablar con un humano', 'atencion humana', 'asesor humano', 'hablar con una persona', 'agente humano']):
        return {
            'respuesta': "¡Por supuesto! Para comunicarte directamente con uno de nuestros asesores de CARAMELL MOMEN S.A.S., puedes escribirnos a:\n\n📧 **Correo de Atención:** contacto@caramellmomen.com\n📞 **Línea Telefónica:** +57 (601) 895-4321\n💬 **WhatsApp Comercial:** +57 300 123 4567\n\nNuestro equipo estará encantado de atender tus solicitudes especiales o resolver cualquier novedad.",
            'derivacion_humana': True,
            'accion_sugerida': 'contacto_asesor'
        }

    # 2. Detección de tareas fuera de propósito (programación, tareas, etc.)
    if any(k in mensaje_lower for k in ['tarea de programacion', 'haz mi tarea', 'codigo python', 'quien es messi', 'resuelve esta ecuacion', 'escribe un ensayo']):
        return {
            'respuesta': "🍬 ¡Hola! Soy **Caramell Assistant**, el asistente virtual de **CARAMELL MOMEN S.A.S.** Estoy especializado exclusivamente en ayudarte con los productos, dulces y compras de nuestra tienda.\n\nNo puedo ayudarte con tareas escolares ni programación, pero si buscas un dulce para consentirte, armar una ancheta o consultar tus compras, ¡cuenta conmigo! 🍭🍫",
            'derivacion_humana': False,
            'accion_sugerida': None
        }

    # 3. Contexto real de datos
    catalog_ctx = get_catalog_context()
    orders_ctx = get_user_orders_context(user_id)
    
    # 4. Si hay API Key de Gemini configurada, llamar a la API
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(Config.GEMINI_MODEL)
            
            prompt_completo = f"""{CARAMELL_SYSTEM_PROMPT}

CONTEXTO EN TIEMPO REAL DE LA BASE DE DATOS:
---
{catalog_ctx}
---
{orders_ctx}
---

MENSAJE DEL CLIENTE:
"{mensaje_usuario}"

Responde con cordialidad, brevedad y exactitud basándote estrictamente en los datos anteriores:"""
            
            response = model.generate_content(prompt_completo)
            if response and response.text:
                return {
                    'respuesta': response.text.strip(),
                    'derivacion_humana': False,
                    'accion_sugerida': None
                }
        except Exception as e:
            print(f"Nota: Fallo llamada API Gemini ({e}). Activando motor inteligente de contingencia.")
            
    # 5. Motor de Reglas Inteligente (Fallback cuando no hay API Key o falla red)
    return motor_reglas_caramell(mensaje_lower, user_id)

def motor_reglas_caramell(texto, user_id):
    """Motor de procesamiento en lenguaje natural local para CARAMELL MOMEN S.A.S."""
    
    # Consulta de pedido
    if 'pedido' in texto or 'mi compra' in texto or 'estado de' in texto:
        if not user_id:
            return {
                'respuesta': "🍭 Para consultar el estado en tiempo real de tus pedidos, por favor **inicia sesión** con tu cuenta de cliente en el menú superior. Así podré mostrarte tus compras de forma segura y personalizada.",
                'derivacion_humana': False,
                'accion_sugerida': 'ir_login'
            }
        pedidos = Pedido.query.filter_by(id_usuario=user_id).order_by(Pedido.fecha_pedido.desc()).limit(3).all()
        if not pedidos:
            return {
                'respuesta': "🍬 Hemos revisado tu cuenta y actualmente no tienes pedidos registrados. ¡Te invito a recorrer nuestro catálogo para endulzar tu día!",
                'derivacion_humana': False,
                'accion_sugerida': 'ver_catalogo'
            }
        resp = "🍬 **Tus Pedidos en CARAMELL MOMEN S.A.S.:**\n\n"
        for p in pedidos:
            resp += f"• **Pedido #{p.id_pedido}** | Total: ${p.total:,.0f} COP\n  **Estado:** `{p.estado}` | Fecha: {p.fecha_pedido.strftime('%d/%m/%Y')}\n"
        resp += "\nPuedes hacer seguimiento completo ingresando a la sección **'Mis Pedidos'**."
        return {'respuesta': resp, 'derivacion_humana': False, 'accion_sugerida': 'mis_pedidos'}

    # Consulta de chocolates
    if 'chocolate' in texto or 'trufa' in texto or 'cacao' in texto:
        chocolates = Producto.query.filter(Producto.nombre.ilike('%chocolate%') | Producto.nombre.ilike('%trufa%')).filter_by(activo=True).all()
        if chocolates:
            resp = "🍫 **¡Nuestros Chocolates Más Populares!**\n\n"
            for c in chocolates[:3]:
                resp += f"• **{c.nombre}**: ${c.precio:,.0f} COP (Disponibles: {c.stock} uds.)\n  _{c.descripcion}_\n\n"
            resp += "¿Te gustaría que te ayude a agregarlos al carrito o buscas algún sabor en particular?"
            return {'respuesta': resp, 'derivacion_humana': False, 'accion_sugerida': 'ver_chocolates'}

    # Consulta de gomitas
    if 'gomita' in texto or 'goma' in texto or 'osito' in texto:
        gomitas = Producto.query.filter(Producto.nombre.ilike('%gomi%') | Producto.nombre.ilike('%goma%')).filter_by(activo=True).all()
        if gomitas:
            resp = "🐻 **¡Gomitas Suaves y Frutales en Caramell Momen!**\n\n"
            for g in gomitas[:3]:
                resp += f"• **{g.nombre}**: ${g.precio:,.0f} COP (Stock: {g.stock} uds.)\n"
            return {'respuesta': resp, 'derivacion_humana': False, 'accion_sugerida': 'ver_gomitas'}

    # Consulta de precios baratos o recomendaciones por presupuesto
    if 'barato' in texto or 'economico' in texto or 'presupuesto' in texto or 'menos de' in texto:
        baratos = Producto.query.filter_by(activo=True).order_by(Producto.precio.asc()).limit(3).all()
        resp = "🍬 **Opciones económicas y deliciosas:**\n\n"
        for b in baratos:
            resp += f"• **{b.nombre}** por solo **${b.precio:,.0f} COP**\n"
        resp += "\n¡Calidad artesanal a precios irresistibles!"
        return {'respuesta': resp, 'derivacion_humana': False, 'accion_sugerida': 'ver_catalogo'}

    # Saludo general o pregunta sobre la tienda
    if any(k in texto for k in ['hola', 'buenas', 'saludos', 'que vendes', 'que productos tienen', 'quienes son']):
        return {
            'respuesta': "🍬 ¡Hola! Bienvenido(a) a **CARAMELL MOMEN S.A.S.**, tu tienda favorita de dulces, confitería y chocolates finos.\n\nPuedo ayudarte a:\n✨ Explorar chocolates, caramelos, gomitas y chupetas.\n✨ Recomendarte opciones según tu presupuesto.\n✨ Consultar precios y existencias en tiempo real.\n✨ Rastrear el estado de tus pedidos.\n\n¿Qué antojo dulce tienes hoy? 🍭",
            'derivacion_humana': False,
            'accion_sugerida': 'explorar'
        }

    # Búsqueda genérica en el catálogo por si mencionó algún dulce
    palabras = texto.replace('?', '').replace('¿', '').split()
    for pal in palabras:
        if len(pal) > 3 and pal not in ['tienen', 'quiero', 'cuanto', 'cuesta', 'precio', 'donde']:
            encontrados = Producto.query.filter(Producto.nombre.ilike(f'%{pal}%'), Producto.activo == True).all()
            if encontrados:
                p = encontrados[0]
                return {
                    'respuesta': f"🍬 ¡Sí, tenemos **{p.nombre}**! Está disponible por **${p.precio:,.0f} COP** y contamos con **{p.stock} unidades** en stock. ¿Deseas agregarlo a tu carrito?",
                    'derivacion_humana': False,
                    'accion_sugerida': 'detalle_producto'
                }

    # Respuesta cordial por defecto
    return {
        'respuesta': "🍭 En **CARAMELL MOMEN S.A.S.** contamos con una amplia variedad de chocolates suizos, caramelos artesanales, gomitas frutales, chupetas y combos festivos.\n\nPuedes explorar todas las opciones en nuestra pestaña de **Catálogo** o preguntarme por cualquier dulce específico que desees encontrar. ¡Estoy aquí para ayudarte! 🍬",
        'derivacion_humana': False,
        'accion_sugerida': 'ver_catalogo'
    }
