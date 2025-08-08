"""
Smart Call Center - Heroku Version
مركز الاتصال الذكي - نسخة Heroku
"""

from flask import Flask, request, Response
import os
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/twilio/voice", methods=['POST', 'GET'])
def handle_twilio_voice():
    """معالجة مكالمات Twilio"""
    
    try:
        logger.info("🎯 === TWILIO VOICE WEBHOOK ===")
        logger.info(f"Method: {request.method}")
        logger.info(f"Form Data: {dict(request.form)}")
        
        # التعامل مع GET requests
        if request.method == 'GET':
            return """
            <h1>✅ Twilio Voice Webhook يعمل!</h1>
            <p>هذا webhook جاهز لاستقبال مكالمات Twilio</p>
            <p>الوقت: {}</p>
            """.format(request.headers.get('Date', 'غير محدد'))
        
        # الحصول على معلومات المكالمة
        call_sid = request.form.get('CallSid', 'unknown')
        from_number = request.form.get('From', 'unknown')
        to_number = request.form.get('To', 'unknown')
        
        logger.info(f"📞 Call SID: {call_sid}")
        logger.info(f"📞 From: {from_number}")
        logger.info(f"📞 To: {to_number}")
        
        # التأكد من صحة الطلب
        if not call_sid or call_sid == 'unknown':
            logger.warning("⚠️ طلب غير صحيح")
            return "Invalid request", 400
        
        # TwiML Response
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar">السلام عليكم ومرحباً بكم في مركز الاتصال الذكي</Say>
    <Pause length="2"/>
    <Say voice="alice" language="ar">النظام يعمل على خادم هيروكو بنجاح</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar">يرجى تسجيل رسالتكم بعد الصوت</Say>
    <Record action="/twilio/recording" method="POST" maxLength="15" playBeep="true" timeout="5"/>
    <Say voice="alice" language="ar">لم نستلم تسجيل. شكراً لاتصالكم</Say>
    <Hangup/>
</Response>'''
        
        logger.info("✅ إرسال TwiML response")
        
        return Response(twiml, mimetype='text/xml; charset=utf-8')
        
    except Exception as e:
        logger.error(f"❌ خطأ في voice handler: {str(e)}")
        
        # رد طارئ
        emergency_twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar">عذراً، حدث خطأ تقني في النظام</Say>
    <Hangup/>
</Response>'''
        
        return Response(emergency_twiml, mimetype='text/xml')

@app.route("/twilio/recording", methods=['POST'])
def handle_twilio_recording():
    """معالجة التسجيلات الصوتية"""
    
    try:
        logger.info("🎤 === RECORDING WEBHOOK ===")
        
        call_sid = request.form.get('CallSid', 'unknown')
        recording_url = request.form.get('RecordingUrl', '')
        recording_duration = request.form.get('RecordingDuration', '0')
        
        logger.info(f"🎤 Call SID: {call_sid}")
        logger.info(f"🎤 Recording URL: {recording_url}")
        logger.info(f"🎤 Duration: {recording_duration} seconds")
        
        # تحليل بسيط للمحتوى (يمكن تطويره لاحقاً)
        response_text = "شكراً لكم. تم استلام رسالتكم بنجاح."
        
        # إذا كان التسجيل طويل، اعتبره استفسار مهم
        if int(recording_duration) > 5:
            response_text += " رسالتكم مهمة وسيتم الرد عليكم قريباً."
        
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar">{response_text}</Say>
    <Pause length="1"/>
    <Say voice="alice" language="ar">مع السلامة</Say>
    <Hangup/>
</Response>'''
        
        logger.info("✅ إرسال recording response")
        
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ خطأ في recording handler: {str(e)}")
        
        simple_response = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="ar">شكراً لكم</Say>
    <Hangup/>
</Response>'''
        
        return Response(simple_response, mimetype='text/xml')

@app.route("/twilio/status", methods=['POST'])
def handle_twilio_status():
    """معالجة حالة المكالمة"""
    
    logger.info("📊 === CALL STATUS ===")
    
    call_sid = request.form.get('CallSid', 'unknown')
    call_status = request.form.get('CallStatus', 'unknown')
    call_duration = request.form.get('CallDuration', '0')
    
    logger.info(f"📊 Call: {call_sid}")
    logger.info(f"📊 Status: {call_status}")
    logger.info(f"📊 Duration: {call_duration}s")
    
    if call_status == 'completed':
        logger.info("✅ مكالمة مكتملة بنجاح")
    elif call_status == 'failed':
        logger.error("❌ فشلت المكالمة")
    
    return "OK"

@app.route("/test")
def test_page():
    """صفحة اختبار"""
    
    return """
    <div style="font-family: Arial; text-align: center; padding: 30px;">
        <h1>🧪 اختبار النظام</h1>
        <p style="color: green; font-size: 20px;">✅ Heroku يعمل بنجاح!</p>
        
        <div style="background: #e8f5e8; padding: 20px; border-radius: 10px; margin: 20px;">
            <h3>📊 معلومات السيرفر:</h3>
            <p><strong>Platform:</strong> Heroku</p>
            <p><strong>Status:</strong> Online ✅</p>
            <p><strong>Response Time:</strong> Fast ⚡</p>
        </div>
        
        <div style="margin: 20px;">
            <a href="/twilio/voice" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">اختبار Voice Webhook</a>
        </div>
    </div>
    """

@app.route("/")
def home():
    """الصفحة الرئيسية"""
    
    return """
    <div style="font-family: Arial; text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh;">
        <h1 style="font-size: 48px; margin-bottom: 20px;">🎯 مركز الاتصال الذكي</h1>
        <h2 style="color: #90EE90; margin-bottom: 30px;">✅ يعمل على Heroku بنجاح!</h2>
        
        <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 30px auto; max-width: 600px; backdrop-filter: blur(10px);">
            <h3 style="color: #FFD700; margin-bottom: 20px;">📞 للاختبار اتصل على:</h3>
            <p style="font-size: 32px; color: #90EE90; font-weight: bold; margin: 20px 0;">+1 570 525 5521</p>
            
            <div style="margin: 30px 0;">
                <h4 style="color: #FFD700;">🎤 ما ستسمعه:</h4>
                <ul style="text-align: right; color: #E0E0E0; font-size: 16px;">
                    <li>رسالة ترحيب بالعربية</li>
                    <li>طلب تسجيل رسالة</li>
                    <li>رد ذكي من النظام</li>
                    <li>إنهاء مهذب للمكالمة</li>
                </ul>
            </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px auto; max-width: 500px;">
            <h4 style="color: #FFD700;">🔧 حالة النظام:</h4>
            <p>✅ Heroku Server: يعمل</p>
            <p>✅ Twilio Webhooks: جاهز</p>
            <p>✅ Voice Processing: نشط</p>
            <p>✅ Arabic Support: مفعل</p>
        </div>
        
        <div style="margin: 30px;">
            <a href="/test" style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-size: 18px; margin: 10px; display: inline-block;">🧪 اختبار النظام</a>
            <a href="/twilio/voice" style="background: #17a2b8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-size: 18px; margin: 10px; display: inline-block;">📞 اختبار Voice</a>
        </div>
        
        <footer style="margin-top: 50px; color: #B0B0B0;">
            <p>🚀 Powered by Heroku | 🎯 Smart Call Center v2.0</p>
        </footer>
    </div>
    """

# تشغيل التطبيق
if __name__ == "__main__":
    # الحصول على port من Heroku
    port = int(os.environ.get("PORT", 5000))
    
    print("🚀 Smart Call Center - Heroku Version")
    print("="*50)
    print("🌐 Running on Heroku!")
    print(f"📡 Port: {port}")
    print("📞 Ready for Twilio calls!")
    print("="*50)
    
    # تشغيل التطبيق
    app.run(host="0.0.0.0", port=port, debug=False)