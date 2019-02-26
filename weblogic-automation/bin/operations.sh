#/bin/bash
set -x
#========================================================================
DEBUG="-v"

# TARGET=audit_admin
: ${HOSTS:="hosts"}
#========================================================================

PATH_ANSIBLE="$(dirname $0)"/..

function help {
    echo "usage: $0 [start|stop|restart] [app_admin|[app_as01|app_as02|...]]"
}

if [[ "$#" -le 1 ]]; then
    help
    exit 1
fi

ACTION=$1
[[ $ACTION =~ [start|stop|restart|clean] ]] || help
shift 1
    
for SRV in "$@"; do
    if [[ "$SRV" =~ "admin" ]]; then
        PLAY_FILE="$PATH_ANSIBLE"/"$ACTION"_admin.yml
    else
        PLAY_FILE="$PATH_ANSIBLE"/"$ACTION"_managed.yml
    fi
    
    if [[ "$ACTION" == "clean" ]]; then
        PLAY_FILE="$PATH_ANSIBLE"/clean.yml
    fi

    # DOMAIN_NAME="${SRV%_*}"    # e.g. audit
    INSTANCE_NAME="${SRV##*_}" # e.g. admin
    
    ansible-playbook \
        $DEBUG \
        -i "$PATH_ANSIBLE"/$HOSTS \
        -l "$SRV" \
        -t "$ACTION" \
        -e server="$INSTANCE_NAME" \
        "$PLAY_FILE"
done