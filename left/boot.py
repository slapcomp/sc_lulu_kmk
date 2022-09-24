import storage
storage.remount("/", readonly=False)
m = storage.getmount("/")
m.label = "SC_LULU_L"
storage.remount("/", readonly=True)
storage.enable_usb_drive()
