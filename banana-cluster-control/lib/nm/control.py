'''
Contains aux application logic
'''

def add_opts(parser):
    # add nonblock mode
    parser.add_option('-n', '--nonblock', help='enable non-blocking mode (useful for scripting)',
                      action='store_const', const=False,
                      default=True, dest='block')
    # add force mode
    parser.add_option('-f', '--force', help='use SIGKILL[9] for stop instead of SIGTERM[15]',
                      action='store_const',
                      default=-1, dest='timeout')
    # add timeout override
    parser.add_option('-t', '--timeout', help='override the timeout value in the config file',
                      metavar='sec', type='int',
                      dest='timeout')
    opt, argv = parser.parse_args()
    return parser, opt, argv
