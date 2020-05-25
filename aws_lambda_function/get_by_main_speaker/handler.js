//carico il db
const connect_to_db = require('./db');

// GET BY TALK HANDLER

//carico il modello dei dati
const talk = require('./talk');

module.exports.get_by_main_speaker = (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    //prendo l'evento, lo traduco in una stringa
    console.log('Received event:', JSON.stringify(event, null, 2));
    //creo il contenuto dove devo mettere i parametri richiesti
    let body = {}
    if (event.body) {
        body = JSON.parse(event.body)
    }
    // set default, tag deve essere definito
    if(!body.main_speaker) {
        callback(null, {
                    statusCode: 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks. Tag is null.'
        })
    }
    //voglio ritornare al massimo 10 risultati per pagina come default
    if (!body.doc_per_page) {
        body.doc_per_page = 10
    }
    //di default restituisco al massimo una pagina
    if (!body.page) {
        body.page = 1
    }
    //invoco la funzione 
    connect_to_db().then(() => {
        console.log('=> get_all talks');
        //skip sposta l indice sulla pagina
        //posso aggiungere filtri mettendo la virgola si tratta di and altrimenti devo specificare dollaro or
        talk.find({main_speaker:{ $regex: body.main_speaker, $options: "i" }})
            .skip((body.doc_per_page * body.page) - body.doc_per_page)
            .limit(body.doc_per_page)
            .then(talks => {
                    callback(null, {
                        statusCode: 200,
                        body: JSON.stringify(talks)
                    })
                }
            )
            .catch(err =>
                callback(null, {
                    statusCode: err.statusCode || 500,
                    headers: { 'Content-Type': 'text/plain' },
                    body: 'Could not fetch the talks.'
                })
            );
    });
};
