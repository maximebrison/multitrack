"""
Framework to easily write MultitrackCore plugins.\n
Documentation can be found here : **insert_doc_link**.
"""

from .MultitrackAPI import MultitrackAPI
from .SerialBridge import SerialBridge
from .SerialDriver import SerialDriver
from .UDPListener import UDPListener
from .models import PluginInfo, BaseActionModel, BaseTextModel, ChannelModel