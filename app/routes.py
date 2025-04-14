# routes.py - Update the imports and define workspace_bp
import random
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Playlist, Link, SharedWorkspace  # Add SharedWorkspace import
from app.forms import RegistrationForm, LoginForm, PlaylistForm, LinkForm, SearchForm, CreateWorkspaceForm, JoinWorkspaceForm, SharePlaylistForm  # Add new forms

# Blueprint definitions
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
playlist_bp = Blueprint('playlist', __name__)
workspace_bp = Blueprint('workspace', __name__)  # Define workspace_bp

# Main routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    search_form = SearchForm()
    query = None
    
    if search_form.validate_on_submit() or request.args.get('query'):
        query = search_form.query.data or request.args.get('query')
        playlists = Playlist.query.filter_by(user_id=current_user.id).\
            filter(Playlist.title.contains(query)).\
            order_by(Playlist.date_created.desc()).all()
    else:
        playlists = Playlist.query.filter_by(user_id=current_user.id).\
            order_by(Playlist.date_created.desc()).all()
    
    return render_template('dashboard.html', playlists=playlists, search_form=search_form, query=query)

@main_bp.route('/mystery')
@login_required
def mystery_link():
    # Get all links from all playlists of the current user
    user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    all_links = []
    
    for playlist in user_playlists:
        links = Link.query.filter_by(playlist_id=playlist.id).all()
        all_links.extend(links)
    
    if not all_links:
        flash('You need to save some links before using Mystery Link Roulette!', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Select a random link
    random_link = random.choice(all_links)
    
    # Redirect to the external URL
    return redirect(random_link.url)

# Authentication routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose a different one.', 'danger')
            return render_template('register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different one.', 'danger')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# Playlist routes
@playlist_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist = Playlist(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(playlist)
        db.session.commit()
        flash('Playlist created successfully!', 'success')
        return redirect(url_for('playlist.view_playlist', playlist_id=playlist.id))
    
    return render_template('playlist_create.html', form=form)

@playlist_bp.route('/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def view_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check if the playlist belongs to the current user
    is_owner = playlist.user_id == current_user.id
    
    # Check if the playlist is shared in any workspace where the user is a member
    has_access = False
    
    if not is_owner:
        # This query checks if there are any workspaces where both:
        # 1. The current user is a member
        # 2. The playlist is shared in that workspace
        shared_workspaces = SharedWorkspace.query.filter(
            SharedWorkspace.members.contains(current_user),
            SharedWorkspace.shared_playlists.contains(playlist)
        ).all()
        
        has_access = len(shared_workspaces) > 0
        
        if not has_access:
            flash("You don't have permission to view this playlist.", "danger")
            return redirect(url_for('main.dashboard'))
    
    links = Link.query.filter_by(playlist_id=playlist_id).order_by(Link.date_added.desc()).all()
    
    # Form for adding new links (only for playlist owner)
    form = None
    if is_owner:
        form = LinkForm()
        if form.validate_on_submit():
            link = Link(
                url=form.url.data,
                title=form.title.data,
                note=form.note.data,
                playlist_id=playlist_id
            )
            db.session.add(link)
            db.session.commit()
            flash('Link added successfully!', 'success')
            return redirect(url_for('playlist.view_playlist', playlist_id=playlist_id))
    
    return render_template('playlist.html', playlist=playlist, links=links, form=form, is_owner=is_owner)

@playlist_bp.route('/<int:playlist_id>/delete')
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check if the playlist belongs to the current user
    if playlist.user_id != current_user.id:
        abort(403)
    
    db.session.delete(playlist)
    db.session.commit()
    flash('Playlist deleted successfully!', 'success')
    return redirect(url_for('main.dashboard'))

@playlist_bp.route('/link/<int:link_id>/delete')
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    playlist_id = link.playlist_id
    
    # Check if the link belongs to a playlist owned by the current user
    playlist = Playlist.query.get_or_404(playlist_id)
    if playlist.user_id != current_user.id:
        abort(403)
    
    db.session.delete(link)
    db.session.commit()
    flash('Link removed successfully!', 'success')
    return redirect(url_for('playlist.view_playlist', playlist_id=playlist_id))

# Add the workspace routes to the file
@workspace_bp.route('/workspace/create', methods=['GET', 'POST'])
@login_required
def create_workspace():
    form = CreateWorkspaceForm()
    if form.validate_on_submit():
        workspace = SharedWorkspace(
            name=form.name.data,
            creator_id=current_user.id
        )
        # Add creator as a member
        workspace.members.append(current_user)
        db.session.add(workspace)
        db.session.commit()
        flash(f'Workspace created! Share code: {workspace.share_code}', 'success')
        return redirect(url_for('workspace.view_workspace', workspace_id=workspace.id))
    
    return render_template('workspace_create.html', form=form)

@workspace_bp.route('/workspace/join', methods=['GET', 'POST'])
@login_required
def join_workspace():
    form = JoinWorkspaceForm()
    if form.validate_on_submit():
        workspace = SharedWorkspace.query.filter_by(share_code=form.share_code.data.upper()).first()
        if not workspace:
            flash('Invalid share code. Please check and try again.', 'danger')
            return render_template('workspace_join.html', form=form)
        
        # Check if already a member
        if current_user in workspace.members:
            flash('You are already a member of this workspace.', 'info')
        else:
            workspace.members.append(current_user)
            db.session.commit()
            flash(f'Successfully joined workspace: {workspace.name}!', 'success')
        
        return redirect(url_for('workspace.view_workspace', workspace_id=workspace.id))
    
    return render_template('workspace_join.html', form=form)

@workspace_bp.route('/workspace/<int:workspace_id>')
@login_required
def view_workspace(workspace_id):
    workspace = SharedWorkspace.query.get_or_404(workspace_id)
    
    # Check if user is a member
    if current_user not in workspace.members:
        abort(403)
    
    return render_template('workspace.html', workspace=workspace)

@workspace_bp.route('/workspace/<int:workspace_id>/share/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def share_playlist(workspace_id, playlist_id):
    workspace = SharedWorkspace.query.get_or_404(workspace_id)
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check permissions
    if current_user not in workspace.members:
        abort(403)
    if playlist.user_id != current_user.id:
        abort(403)
    
    # Add playlist to workspace
    if playlist not in workspace.shared_playlists:
        workspace.shared_playlists.append(playlist)
        db.session.commit()
        flash('Playlist shared successfully!', 'success')
    else:
        flash('This playlist is already shared in this workspace.', 'info')
    
    return redirect(url_for('workspace.view_workspace', workspace_id=workspace_id))

@workspace_bp.route('/workspace/<int:workspace_id>/unshare/<int:playlist_id>')
@login_required
def unshare_playlist(workspace_id, playlist_id):
    workspace = SharedWorkspace.query.get_or_404(workspace_id)
    playlist = Playlist.query.get_or_404(playlist_id)
    
    # Check permissions
    if current_user not in workspace.members:
        abort(403)
    if playlist.user_id != current_user.id:
        abort(403)
    
    # Remove playlist from workspace
    if playlist in workspace.shared_playlists:
        workspace.shared_playlists.remove(playlist)
        db.session.commit()
        flash('Playlist removed from workspace.', 'success')
    
    return redirect(url_for('workspace.view_workspace', workspace_id=workspace_id))