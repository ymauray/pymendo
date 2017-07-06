<?php
use Psr\Http\Message\ServerRequestInterface;
use Psr\Http\Message\ResponseInterface;

require '../vendor/autoload.php';

use Medoo\Medoo;

$database = new Medoo([
    'database_type' => 'mysql',
    'database_name' => 'pymendo',
    'server' => 'localhost',
    'username' => 'pymendo',
    'password' => 'pymendo',
    'charset' => 'utf8',
]);

$app = new \Slim\App;
$app->get("/backlog", function (ServerRequestInterface  $request, ResponseInterface  $response) {
    global $database;
    $data = $database->select('quick_album',
        ['id', 'name', 'artist_id', 'artist_name', 'single', 'releasedate', 'image'], [
            'ORDER' => ["releasedate" => "DESC", "single" => "ASC", "id" => "DESC"],
            'LIMIT' => 60
        ]);

    $response = $response->withHeader('Content-Type', 'application/json');
    $response->getBody()->write(json_encode($data));
    return $response;
});
$app->get("/album/{id}/{single}", function (ServerRequestInterface  $request, ResponseInterface  $response) {
    global $database;
    $id = $request->getAttribute("id");
    $single = $request->getAttribute("single");
    $data = $database->select('quick_album',
        ['id', 'name', 'artist_id', 'artist_name', 'single', 'releasedate', 'image'], [
            'id' => $id,
            'single' => $single,
        ]);
    $result['album'] = $data[0];
    if ($single) {
        $data = $database->select('tracks',
            ['track_name', 'artist_name', 'image', 'audio', 'audiodownload', 'shorturl'], [
                'id' => $id,
            ]);
        $result['tracks'] = $data;
    }
    else {
        $data = $database->select('tracks',
            ['track_name', 'artist_name', 'image', 'audio', 'audiodownload', 'shorturl'], [
                'album_id' => $id,
            ]);
        $result['tracks'] = $data;
    }

    $response = $response->withHeader('Content-Type', 'application/json');
    $response->getBody()->write(json_encode($result));
    return $response;
});

/**
 * Reject : rejeter un album ou un single
 */
$app->get("/reject/{id}/{single}", function(ServerRequestInterface $request, ResponseInterface $response) {
    global $database;
    $id = $request->getAttribute("id");
    $single = $request->getAttribute("single");
    $ids = [];
    $data = null;
    if ($single == "0") {
        $ids = $database->select("tracks", ["id"], ["album_id" => $id]);
    }
    else {
        $ids[] = ["id" => $id];
    }
    $response = $response->withHeader('Content-Type', 'application/json');
    $response->getBody()->write(json_encode($ids));
    return $response;
});

$app->run();
