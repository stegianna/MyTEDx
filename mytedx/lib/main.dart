import 'package:flutter/material.dart';
import 'talk_repository.dart';
import 'models/talk.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MyTEDx',
      theme: ThemeData(
        primarySwatch: Colors.red,
      ),
      home: MyHomePage(title: 'MyTEDx'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _controller = TextEditingController();
  bool visibilityTag = false;
  bool visibilitySpeaker = false;
  Future<List<Talk>> _talks;
  int page = 1;

  @override
  void initState() {
    super.initState();
  }

  void _changed(bool visibility, String field) {
    setState(() {
      if (field == "tag"){
        visibilityTag = visibility;
      }
      if (field == "speaker"){
        visibilitySpeaker = visibility;
      }
    });
  }

  void _getTalksByTag() async {
    setState(() {
      _talks = getTalksByTag(_controller.text, page);
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My TedX App',
      theme: ThemeData(
        primarySwatch: Colors.red,
      ),
      home: Scaffold(
        appBar: AppBar(
          title: Text('My TEDx App'),
        ),
        body: new Container(
          child: (_talks == null)
          ? ListView(
              children: <Widget>[
                new Container(
                  margin: new EdgeInsets.all(20.0),
                  child: new FlutterLogo(size: 150.0, colors: Colors.red),
                ),
                new Container(
                  height: 80.0,
                ),
                new Container(
                  margin: new EdgeInsets.only(left: 16.0, right: 16.0),
                  child: new Column(
                    children: <Widget>[
                      visibilitySpeaker ? new Row(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: <Widget>[
                          new Expanded(
                            flex: 11,
                            child: new TextField(
                              maxLines: 1,
                              controller: _controller,
                              decoration: new InputDecoration(
                                hintText: "Enter main speaker",
                                isDense: false
                              ),
                            ),
                          ),
                          new Expanded(
                            flex: 1,
                            child: new IconButton(
                              color: Colors.grey[600],
                              icon: const Icon(Icons.search, size: 22.0),
                              onPressed: (){
                                _getTalksByTag();
                              }
                            ),
                          )
                        ],
                      ) : 

                      new Row(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: <Widget>[ 
                          new Expanded(
                            flex: 11,
                            child: new TextField(
                              maxLines: 1,
                              controller: _controller,
                              decoration: new InputDecoration(
                                hintText: "Enter tag",
                                isDense: false
                              ),
                            ),
                          ),
                          new Expanded(
                            flex: 1,
                            child: new IconButton(
                              color: Colors.grey[600],
                              icon: const Icon(Icons.search, size: 22.0),
                              onPressed: (){
                                _getTalksByTag();
                              }
                            ),
                          )
                        ],
                      )
                    ],
                  )
                ),
                new Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: <Widget>[
                    new InkWell(
                      onTap: (){
                        visibilitySpeaker ? null : _changed(true, "speaker"); _changed(false, "tag");
                      },
                      child: new Container(
                        margin: new EdgeInsets.only(top: 16.0),
                        child: new Column(
                          children: <Widget>[
                            new Icon(Icons.mic, color: visibilitySpeaker ? Colors.grey[400] : Colors.grey[600]),
                            new Container(
                              margin: const EdgeInsets.only(top: 8.0),
                              child: new Text(
                                "Main Speaker",
                                style: new TextStyle(
                                  fontSize: 12.0,
                                  fontWeight: FontWeight.w400,
                                  color: visibilitySpeaker ? Colors.grey[400] : Colors.grey[600],
                                ),
                              ),
                            ),
                          ],
                        ),
                      )
                    ),
                    new SizedBox(width: 24.0),
                    new InkWell(
                      onTap: (){
                        visibilityTag ? null : _changed(true, "tag"); _changed(false, "speaker");
                      },
                      child: new Container(
                        margin: new EdgeInsets.only(top: 16.0),
                        child: new Column(
                          children: <Widget>[
                            new Icon(Icons.local_offer, color: visibilityTag ? Colors.grey[400] : Colors.grey[600]),
                            new Container(
                              margin: const EdgeInsets.only(top: 8.0),
                              child: new Text(
                                "Tag",
                                style: new TextStyle(
                                  fontSize: 12.0,
                                  fontWeight: FontWeight.w400,
                                  color: visibilityTag ? Colors.grey[400] : Colors.grey[600],
                                ),
                              ),
                            )
                          ],
                        ),
                      )
                    )
                  ],
                )
              ],
            )
          : new Container(
              alignment: Alignment.center,
              padding: const EdgeInsets.all(8.0),
              child: FutureBuilder<List<Talk>>(
                  future: _talks,
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      return Scaffold(
                          appBar: AppBar(
                            title: Text("#" + _controller.text),
                          ),
                          body: ListView.builder(
                            itemCount: snapshot.data.length,
                            itemBuilder: (context, index) {
                              return GestureDetector(
                                child: ListTile(
                                    subtitle:
                                        Text(snapshot.data[index].mainSpeaker),
                                    title: Text(snapshot.data[index].title)),
                                onTap: () => Scaffold.of(context).showSnackBar(
                                    SnackBar(content: Text(snapshot.data[index].details))),
                              );
                            },
                          ),
                          floatingActionButtonLocation:
                              FloatingActionButtonLocation.centerDocked,
                          floatingActionButton: FloatingActionButton(
                            child: const Icon(Icons.arrow_drop_down),
                            onPressed: () {
                              if (snapshot.data.length >= 6) {
                                page = page + 1;
                                _getTalksByTag();
                              }
                            },
                          ),
                          bottomNavigationBar: BottomAppBar(
                            child: new Row(
                              mainAxisSize: MainAxisSize.max,
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: <Widget>[
                                IconButton(
                                  icon: Icon(Icons.home),
                                  onPressed: () {
                                    setState(() {
                                      _talks = null;
                                      page = 1;
                                      _controller.text = "";
                                    });
                                  },
                                )
                              ],
                            ),
                          ));
                    } else if (snapshot.hasError) {
                      return Text("${snapshot.error}");
                    }

                    return CircularProgressIndicator();
                  },
                ),
            )
        )
      )
    );
  }
}