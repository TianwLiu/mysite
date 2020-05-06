from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
import tool.routing
application=ProtocolTypeRouter({
    'websocket':AuthMiddlewareStack(
        URLRouter(
            tool.routing.websocket_urlpatterns
        )
    )
})