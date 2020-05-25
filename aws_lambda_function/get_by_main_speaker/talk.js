const mongoose = require('mongoose');

const talk_schema = new mongoose.Schema({
    _id:String,
    main_speaker: String,
    title: String,
    posted: String,
    url: String,
    tags: Array,
    next_talks: Array,
}, { collection: 'tedz_data' });

//talk rappresenta il nome del modello
module.exports = mongoose.model('talk', talk_schema);