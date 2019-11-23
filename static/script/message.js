document.addEventListener('DOMContentLoaded',function(){

        var socket = io.connect('http://127.0.0.1:5000');
        var socket = io.connect('http://' + document.domain + ':' + location.port);//127.0.0.1:5000');

        var view = document.getElementById ('message_board')
        var text = document.getElementById('text')
        var active_chat = from_redirect

        socket.on('connect', ()=>{
           // socket.send("we are connected");
        })

        socket.on('message', data =>{
            var p = document.createElement('p')
            var br = document.createElement('br')
            console.log(data)
            p.innerHTML = data.text +'<span style=" color:blue;">  :'+data.username+'</span>'
            view.append(p) 
        })

        document.getElementById('sent').onclick = (e)=>{
            console.log(` i am ${user}`)
         socket.send({'text':text.value,'username':user} )
         text.value = '';
     }

        document.querySelectorAll('.current_chats').map(list=>{
                list.onclick=(e)=>{
                let newChat = list.innerHTML
                if( newChat == active_chat ){
                    msg = `you're currently chatting with ${active_chat}`;
                    tellUser(msg)
                }else{
                    leaveRoom(active_chat)
                    joinRoom(newChat)
                   // msg = `you're now chatting with ${active_chat} communicate clearly`;
                    active_chat == newChat;
                }

                             }
                     })

        socket.on('join',()=>{
            socket.emit({'username' :user, 'active_chat':active_chat})
        })
        socket.on('leave',()=>{
            socket.emit({'username' :user, 'active_chat':active_chat})
        })

})


