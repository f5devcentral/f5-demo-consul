when HTTP_REQUEST {
    # Make sure this is the credentials monitor
    if { [HTTP::uri] == "/credentials" } {
        if { [HTTP::header exists Authorization] } {
            set decoded_secret [findstr [b64decode [findstr [HTTP::header Authorization] "Basic " 6]] "user:" 5]

            # Create/update table entry
            table set consul_secret_key $decoded_secret indefinite
            # Respond so monitor is up
            HTTP::respond 200
        } else {
           HTTP::respond 200
            #set decoded_secret [table lookup consul_secret_key]
            #HTTP::respond 200 content $decoded_secret
        }
    } else {
    set decoded_secret [table lookup consul_secret_key]
        HTTP::header insert X-Consul-Token $decoded_secret
    }
    #set client_ip [IP::client_addr]
    #HTTP::respond 404 content "not found $client_ip"
}
