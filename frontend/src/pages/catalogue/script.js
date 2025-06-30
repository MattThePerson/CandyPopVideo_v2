

query = {
    query_type: 'performers',    //  str = [ performers | studios ]
    query_string: null,          //  str|None
    use_sort_performers: false,  //  bool
    filter_performer: null,      //  str|None
    filter_studio: null,         //  str|None
    filter_collection: null,     //  str|None
    filter_tag: null,            //  str|None
}

console.log('requesting catalogue ...');
makeApiRequestPOST_JSON('api/query/get/catalogue', query, response => {
    console.log('recieved!');
    console.log(response);
})
