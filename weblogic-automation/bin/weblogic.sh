#/bin/bash
set -x
#========================================================================
DEBUG="-v"

# TARGET=audit_admin
: ${HOSTS:="hosts"}
#========================================================================

PATH_ANSIBLE="$(dirname $0)"/..

function help {
    echo "usage: $0 [install] [app_admin|[app_as01|app_as02|...]]"
}

if [[ "$#" -le 1 ]]; then
    help
    exit 1
fi

ACTION=$1
[[ $ACTION =~ [install] ]] || help
shift 1
    
for SRV in "$@"; do
    # if [[ "$SRV" =~ "admin" ]]; then
        # PLAY_FILE="$PATH_ANSIBLE"/"$ACTION"_admin.yml
    # else
        # PLAY_FILE="$PATH_ANSIBLE"/"$ACTION"_managed.yml
    # fi
    
    if [[ "$ACTION" == "install" ]]; then
        PLAY_FILE="$PATH_ANSIBLE"/install_weblogic.yml
    fi

    # DOMAIN_NAME="${SRV%_*}"    # e.g. audit
    # INSTANCE_NAME="${SRV##*_}" # e.g. admin
    
    ansible-playbook \
        $DEBUG \
        -i "$PATH_ANSIBLE"/$HOSTS \
        -l "$SRV" \
        "$PLAY_FILE"
done