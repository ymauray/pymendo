<?php
use Medoo\Medoo;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\ServerRequestInterface;

require '../vendor/autoload.php';

$database = new Medoo([
    'database_type' => 'mysql',
    'database_name' => 'pymendo',
    'server' => 'localhost',
    'username' => 'pymendo',
    'password' => 'pymendo',
    'charset' => 'utf8',
]);

$app = new \Slim\App;
$app->get("/backlog", function (ServerRequestInterface $request, ResponseInterface $response) {
    global $database;
    /*
    $data = $database->select('quick_album',
        ['id', 'name', 'artist_id', 'artist_name', 'single', 'releasedate', 'image'], [
            'ORDER' => ["releasedate" => "DESC", "single" => "ASC", "id" => "DESC"],
            'LIMIT' => 60
        ]);
    */
    $data = $database->query("SELECT * FROM quick_album qa LEFT JOIN tags t ON t.track_id = CONCAT('1', qa.single, qa.id) HAVING tag_type IS null OR tag_type != 'pymendo' ORDER BY releasedate DESC, single ASC, id DESC LIMIT 60;")->fetchAll();
    $response = $response->withHeader('Content-Type', 'application/json');
    $response->getBody()->write(json_encode($data));
    return $response;
});
$app->get("/album/{id}/{single}", function (ServerRequestInterface $request, ResponseInterface $response) {
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
    } else {
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
$app->get("/reject/{id}/{single}", function (ServerRequestInterface $request, ResponseInterface $response) {
    global $database;
    $id = $request->getAttribute("id");
    $single = $request->getAttribute("single");
    $database->delete("tags", ["AND" => ["tag_type" => "pymendo", "track_id" => "1" . $single . $id]]);
    $database->insert("tags", ["track_id" => "1" . $single . $id, "tag_type" => "pymendo", "tag_value" => "rejectedsss"]);
    $response = $response->withHeader('Content-Type', 'application/json');
    $response->getBody()->write(json_encode($ids));
    return $response;
});

$app->run();
