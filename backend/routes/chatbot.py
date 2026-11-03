from flask import Blueprint, request, jsonify, session
from backend.services.gemini_service import responder_con_gemini

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot')

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    mensaje = data.get('mensaje', '').strip()
    
    if not mensaje:
        return jsonify({
            'success': False,
            'message': 'El mensaje no puede estar vacío'
        }), 400
        
    user_id = session.get('id_usuario')
    
    resultado = responder_con_gemini(mensaje, user_id=user_id)
    
    return jsonify({
        'success': True,
        'respuesta': resultado['respuesta'],
        'derivacion_humana': resultado.get('derivacion_humana', False),
        'accion_sugerida': resultado.get('accion_sugerida')
    })
