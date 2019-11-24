document.addEventListener('DOMContentLoaded',function(){

        //var socket = io.connect('http://localhost:5000');
        var socket = io.connect('http://' + document.domain + ':' + location.port);//127.0.0.1:5000');

        var view = document.getElementById ('message_board')
        var text = document.getElementById('text')
        var active_chat = from_redirect;

        socket.on('message', data =>{
            var p = document.createElement('h1')
            p.style.width = '30%';
            var br = document.createElement('br')
            console.log(active_chat+"this is active")
            if(data.username == user)
             p.innerHTML = data.text +'<span style=" color:blue;">  :'+data.username+'</span>'
            view.append(p) 
        })

        document.getElementById('sent').onclick = (e)=>{
            console.log(` i am ${user}`)
        alert(active_chat)
        if(!active_chat) return alert("you've not specified any one to chat with")
         socket.send({'text':text.value,'username':user} )
         text.value = '';
         text.focus()
     }

        document.querySelectorAll('.current_chats').forEach(list=>{
                if( list.innerHTML == from_redirect){
                    list.style.background = 'darkgrey'
                }
                list.onclick=(e)=>{
                let newChat = list.innerHTML
                console.log(newChat)
                if( newChat == active_chat ){
                    msg = `you're currently chatting with ${active_chat}`;
                    tellUser(msg)
                }else{
                    
                    recommendation.style.display = 'block';
                    leaveRoom(active_chat)
                    joinRoom(newChat)
                    active_chat = newChat;
                    msg = `you're now chatting with ${active_chat} communicate clearly`;
                    view.innerHTML = "";
                    tellUser(msg)
                    
                }

                             }
                     })
        leaveRoom = ()=>{
            socket.emit({'username' :user, 'active_chat':active_chat})
        }
        
        joinRoom = ()=>{
            socket.emit({'username' :user, 'active_chat':active_chat})
        }
       
        function tellUser(msg){
            var p = document.createElement('p')
            p.innerHTML = msg
            console.log(p)
            view.append(p)
        }

})


