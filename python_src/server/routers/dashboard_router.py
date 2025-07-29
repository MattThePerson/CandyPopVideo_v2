# from fastapi import APIRouter, WebSocket
# from fastapi.websockets import WebSocketDisconnect
# import shlex
# import asyncio

# from manager import backend_manager, create_argument_parser


# dashboard_router = APIRouter()


# @dashboard_router.websocket("/terminal")
# async def websocket_terminal_endpoint(websocket: WebSocket):
#     """  """
#     await websocket.accept()
#     parser = create_argument_parser(non_exiting=True)
#     task = None

#     async def backend_task(args_, ws):
#         """ run backend task as a cancellable task """
#         try:
#             await backend_manager(args_, ws)
#         except asyncio.CancelledError:
#             print('Task cancelled')
#             await websocket.send_text('Task cancelled')
#             raise
    
#     try:
#         while True:
            
#             text_recieved = await websocket.receive_text()
#             if '--help' in text_recieved or '-h' in text_recieved:
#                 print(parser.format_help())
#                 await websocket.send_text(parser.format_help())
                
#             elif text_recieved == '__INTERRUPT__':
#                 print('interrupt recieved')
#                 if task and not task.done():
#                     task.cancel()
#                     await websocket.send_text('Cancelling task ...')
#             else:
#                 args = None
#                 try:
#                     args = parser.parse_args(shlex.split(text_recieved))
#                 except Exception as e:
#                     await websocket.send_text(str(e))
#                     continue

#                 if args:
#                     task = asyncio.create_task(backend_task(args, websocket))
#                     await task

#     except WebSocketDisconnect:
#         print("Client disconnected")


